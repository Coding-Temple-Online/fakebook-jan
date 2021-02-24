import stripe
from flask_login import current_user
from app.blueprints.shop.models import Cart

class Session:
    @classmethod
    def create_session(cls, cart=None):
        cart = Cart.query.filter_by(user_id=current_user.id).all()
        display_cart = cls.build_cart(cart=cart)
        items = []
        for item in display_cart.values():
            new_dict = {
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                            'name': item['name'],
                            },
                            'unit_amount': int(item['price'] * 100),
                        },
                        'quantity': item['quantity'],
                    }
            items.append(new_dict)
        return stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=items,
            customer_email=current_user.email,
            mode='payment',
            success_url='http://localhost:5000/shop/cart/checkout/success',
            cancel_url='http://localhost:5000/shop/cart'
        )

    @classmethod
    def build_cart(cls, cart=None):
        from app.blueprints.shop.models import Product, Cart
        
        cart_list = {}
        if cart is None:
            cart = []
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
        return cart_list

    @classmethod
    def get_session(cls, data):
        return stripe.checkout.Session.retrieve(data)