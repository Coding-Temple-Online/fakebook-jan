from .import bp as shop_bp
from flask import render_template, redirect, url_for, flash, request
from app.blueprints.shop.models import Product, Cart
from flask_login import current_user
from app import db

@shop_bp.route('/')
def home():
    context = {
        'products': Product.query.all()
    }
    return render_template('shop/home.html', **context)

@shop_bp.route('/product/add')
def add_product():
    try:
        _id = request.args.get('id')
        p = Product.query.get(_id)
        c = Cart(user_id=current_user.id, product_id=p.id)
        c.save()
        flash(f'{p.name} was added successfully', 'success')
    except Exception as error:
        print(error)
        flash(f'{p.name} was not added successfully. Try again.', 'danger')
    return redirect(url_for('shop.home'))

@shop_bp.route('/cart')
def cart():
    context = {}
    return render_template('shop/cart.html', **context)


@shop_bp.route('/cart/update', methods=['GET', 'POST'])
def update_product():
    p = Product.query.get(request.args.get('product_id'))
    cart = current_user.cart
    res = request.form
    num_update = int(res['update_num'])
    counter1 = Cart.query.filter_by(user_id=current_user.id).count()
    var1 = Cart.query.filter_by(user_id=current_user.id).count()
    counter2 = 0
    tobe_Deleted = Cart.query.filter_by(user_id=current_user.id).count() - num_update
    tobe_Added = Cart.query.filter_by(user_id=current_user.id).count() + num_update

    for i in cart:
        if i.product_id == p.id and current_user.id == i.user_id:
            if num_update > Cart.query.filter_by(user_id=current_user.id).count():
                while counter1 != tobe_Added-var1:
                    c = Cart(user_id=current_user.id, product_id=p.id)
                    c.save()
                    counter1 += 1
                break
            elif num_update < Cart.query.filter_by(user_id=current_user.id).count():
                while counter2 != tobe_Deleted:
                    cart_item = Cart.query.filter_by(user_id=current_user.id).first()
                    db.session.delete(cart_item)
                    counter2 += 1
                    break

    db.session.commit()
    flash(f'Cart Updated', 'info')
    return redirect(url_for('shop.cart'))


# @shop_bp.route('/cart/add', methods=['GET', 'POST'])
# def add_product():
#     p = Product.query.get(request.args.get('product_id'))
#     cart = current_user.cart
#     res = request.form
#     num_delete = int(res['delete_num'])
#     counter = 0
#     for i in cart:
#         if i.product_id == p.id and current_user.id == i.user_id:
#             while counter < num_delete:
#                 cart_item = Cart.query.filter_by(
#                     user_id=current_user.id).first()
#                 db.session.delete(cart_item)
#                 counter += 1
#                 break
#     db.session.commit()
#     flash(f'Product deleted', 'info')
#     return redirect(url_for('shop.cart'))

@shop_bp.route('/checkout')
def checkout():
    context = {}
    return render_template('shop/checkout.html', **context)
