from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import UUID
import shortuuid
from app.blueprints.blog.models import Post

# [id, a, b]
# [1, 1, 5]
# [2, 3, 1]
# [3, 3, 2]

followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
    )

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    is_stripe_customer = db.Column(db.Boolean, default=False)
    posts = db.relationship('Post', cascade='all, delete-orphan', backref='user', lazy=True)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )
    cart = db.relationship('Cart', cascade='all, delete-orphan', backref='user', lazy=True)

    def __init__(self, first_name, last_name, password):
        super().__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.password = password
        self.email = f'{self.first_name}{self.last_name[0]}@codingtemple.com'.lower()


    def make_stripe_customer(self):
        pass

    def followed_posts(self):
        followed = Post.query.join(
            followers,
            (followers.c.followed_id == Post.user_id)
        ).filter(followers.c.follower_id == self.id)
        self_posts = Post.query.filter_by(user_id=self.id)
        all_posts = followed.union(self_posts).order_by(Post.date_created.desc())
        return all_posts


    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            db.session.commit()

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            db.session.commit()

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def create_password_hash(self, password):
        self.password = generate_password_hash(password)

    def verify_password_hash(self, password_to_verify):
        return check_password_hash(self.password, password_to_verify)

    def save(self):
        self.create_password_hash(self.password)
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f'<User: {self.email}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)