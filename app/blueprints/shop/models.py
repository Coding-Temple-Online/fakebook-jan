from app import db
from datetime import datetime as dt

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    price = db.Column(db.Float)
    tax = db.Column(db.Float)
    date_created = db.Column(db.DateTime, default=dt.utcnow)
    date_updated = db.Column(db.DateTime)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'tax': self.tax,
            'date_created': self.date_created,
            'date_updated': self.date_updated,
        }
        return data

    def from_dict(self, data):
        for field in ['name', 'description', 'price']:
            if field in data:
                setattr(self, field, data[field])
        self.tax = round(self.price * .06, 2)

    def __repr__(self):
        return f'{self.name} @{self.price}'

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    user_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.ForeignKey('product.id'), nullable=False)
    date_added = db.Column(db.DateTime, default=dt.utcnow)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        from app.blueprints.auth.models import User
        return f'<Cart: {User.query.get(self.user_id).email}: {Product.query.get(self.product_id).name}>'

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    user_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.ForeignKey('product.id'), nullable=False)
    date_filled = db.Column(db.DateTime, default=dt.utcnow)

    def save(self):
        db.session.add(self)
        db.session.commit()