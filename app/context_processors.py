from flask import current_app as app
from flask_login import current_user
from app.blueprints.shop.models import Cart, Product
from functools import reduce


@app.context_processor
def get_cart_stuff():
    return {
        'stripeKey': app.config.get('STRIPE_TEST_KEY')
    }

@app.context_processor
def display_cart_info():
    if not current_user.is_authenticated or current_user is None or not current_user.cart:
        return {
                'cart': {
                    'items': [],
                    'display_cart': [],
                    'tax': float(0.00),
                    'subtotal': float(0.00),
                    'grand_total': float(0.00),
                } 
            }
    else:
        from app.stripe.session import Session
        
        cart = Cart.query.filter_by(user_id=current_user.id).all()
        cart_list = Session.build_cart(cart)
        return {
                'cart': {
                    'items': cart,
                    'display_cart': cart_list.values(),
                    'tax': round(reduce(lambda x,y:x+y, [Product.query.filter_by(id=cart_item.product_id).first().tax for cart_item in cart]), 2) if cart else float(0),
                    'subtotal': round(reduce(lambda x,y:x+y, [Product.query.filter_by(id=cart_item.product_id).first().price for cart_item in cart]), 2) if cart else float(0),
                    'grand_total': round(reduce(lambda x,y:x+y, [Product.query.filter_by(id=cart_item.product_id).first().price + Product.query.filter_by(id=cart_item.product_id).first().tax for cart_item in cart]), 2) if cart else float(0),
                } 
            }