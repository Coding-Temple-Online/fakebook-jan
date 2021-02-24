from .import bp as shop_bp
from flask import render_template, redirect, url_for, flash, request, current_app as app, jsonify, session
from app.blueprints.shop.models import Product, Cart
from flask_login import current_user, login_required
from app import db
from app import stripe as my_stripe
from app.stripe.session import Session
import os

# [<Cart: derekh@codingtemple.com: Dingy Brown T-Shirt>, <Cart: derekh@codingtemple.com: Dingy Brown T-Shirt>, <Cart: derekh@codingtemple.com: Dingy Brown T-Shirt>, <Cart: derekh@codingtemple.com: Dingy Brown T-Shirt>, <Cart: derekh@codingtemple.com: Dingy Brown T-Shirt>, <Cart: derekh@codingtemple.com: Dingy Brown T-Shirt>, <Cart: derekh@codingtemple.com: Black T-Shirt>, <Cart: derekh@codingtemple.com: Black T-Shirt>, <Cart: derekh@codingtemple.com: Black T-Shirt>, <Cart: derekh@codingtemple.com: Black T-Shirt>]
def find_product(product_to_find, a_cart):
    for obj in a_cart:
        if obj.product_id == product_to_find.id:
            return obj

@login_required
@shop_bp.route('/')
def home():
    context = {
        'products': Product.query.all()
    }
    return render_template('shop/home.html', **context)

@login_required
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

@login_required
@shop_bp.route('/cart')
def cart():
    context = {}
    return render_template('shop/cart.html', **context)

@login_required
@shop_bp.route('/cart/delete')
def delete_product():
    p = Product.query.get(request.args.get('product_id'))
    cart = current_user.cart
    for i in cart:
        if i.product_id == p.id and current_user.id == i.user_id:
            cart_item = Cart.query.filter_by(user_id=current_user.id).first()
            db.session.delete(cart_item)
    db.session.commit()
    flash(f'Product deleted', 'info')
    return redirect(url_for('shop.cart'))

@login_required
@shop_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    checkout_session = Session.create_session()
    session['checkout_session_id'] = checkout_session.id
    flash('Your payment was successful.', 'success')
    return redirect(url_for('shop.checkout_success'))

@login_required
@shop_bp.route('/cart/checkout/success')
def checkout_success():
    checkout_session = Session.get_session(session.get('checkout_session_id'))
    print(checkout_session)

    # customer = stripe.Customer.retrieve(session.customer)
    # print(customer)
    context = {
        'checkout_session': checkout_session
    }
    # At some point, add more functionality
    # [db.session.delete(i) for i in Cart.query.filter_by(user_id=current_user.id).all()]
    # db.session.commit()
    return render_template('shop/checkout-success.html', **context)

@login_required
@shop_bp.route('/cart/update')
def update_cart():
    # Get the user's cart
    cart = Cart.query.filter_by(user_id=current_user.id).all()
    # Find the product you want to remove
    product_to_remove = Product.query.get(request.args.get('product_id'))
    # Find the quantity you  want to change it to
    quantity = int(request.args.get('quantity'))
    # If the form quantity is less/more than the quantity inside the display_cart
    display_cart = Session.build_cart(cart=cart)
    # {15: {'id': 97, 'product_id': 15, 'quantity': 4, 'name': 'Black T-Shirt', 'description': 'This is a nice shirt!', 'price': 15.99, 'tax': 0.96}

    # loop over the display cart
    counter = 0
    for i in display_cart.values():
        if i['product_id'] == product_to_remove.id:
            if quantity < i['quantity'] and quantity != 0:
                while counter < i['quantity'] - quantity:
                    for item in cart:
                        if product_to_remove.id == i['product_id']:
                            cart_item = Cart.query.filter_by(product_id=product_to_remove.id).first()
                            db.session.delete(cart_item)
                        break
                    counter+=1
                db.session.commit()
            elif i['quantity'] < quantity  and quantity != 0:
                new_items = []
                for _ in range(quantity - i['quantity']):
                    cart_item = Cart(user_id=current_user.id, product_id=product_to_remove.id)
                    new_items.append(cart_item)
                db.session.add_all(new_items)
                db.session.commit()
            elif quantity == 0:
                [db.session.delete(ci) for ci in cart if ci.product_id == i['product_id']]
                db.session.commit()
                flash('Item removed successfully.', 'success')
                return redirect(url_for('shop.cart'))
    flash('Item updated successfully.', 'success')
    return redirect(url_for('shop.cart'))