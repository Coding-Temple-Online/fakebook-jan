from flask import current_app as app
from flask_login import current_user
from app.blueprints.shop.models import Cart, Product
from functools import reduce


@app.context_processor
def display_cart_info():
    if not current_user.is_authenticated or not Cart.query.all():
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
        cart_list = {}
        cart = Cart.query.filter_by(user_id=current_user.id).all()
        if len(cart) > 0:
            for i in cart:
                p = Product.query.get(i.product_id)
                if i.product_id not in cart_list.keys():
                    cart_list[p.id] = {
                        'id': i.id,
                        'product_id': p.id,
                        'quantity': 1,
                        'name': p.name,
                        'description': p.description,
                        'price': p.price,
                        'tax': p.tax
                    }
                else:
                    cart_list[p.id]['quantity'] += 1
        print(cart_list)
        return {
            'cart': {
                'items': cart,
                'display_cart': cart_list.values(),
                'tax': round(reduce(lambda x, y: x+y, [i['tax'] for i in cart_list.values()]), 2),
                'subtotal': round(reduce(lambda x, y: x+y, [i['price'] for i in cart_list.values()]), 2),
                'grand_total': round(reduce(lambda x, y: x+y, [i['price'] + i['tax'] for i in cart_list.values()]), 2),
            }
        }
