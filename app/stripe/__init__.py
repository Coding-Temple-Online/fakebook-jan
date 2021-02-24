import stripe
from flask import current_app as app

stripe_key = {
    'publishable_key': app.config.get('STRIPE_TEST_KEY'),
    'secret_key': app.config.get('STRIPE_SECRET_KEY')
}

stripe.api_key = stripe_key['secret_key']