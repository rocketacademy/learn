from django.conf import settings
from sentry_sdk import capture_exception, capture_message
import stripe


class Stripe:
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def create_coupon(self, discount):
        try:
            if discount['type'] == 'percent':
                stripe_coupon = stripe.Coupon.create(
                    percent_off=discount['amount'],
                    duration='forever'
                )
            elif discount['type'] == 'dollars':
                stripe_coupon = stripe.Coupon.create(
                    amount_off=discount['amount'] * 100,
                    duration='forever',
                    currency=settings.SINGAPORE_DOLLAR_CURRENCY
                )

            return stripe_coupon
        except Exception as error:
            capture_message(f"Exception when calling stripe.Coupon.create with {discount}")
            capture_exception(error)
