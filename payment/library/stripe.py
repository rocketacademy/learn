from django.conf import settings
from sentry_sdk import capture_exception, capture_message
import stripe


class Stripe:
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def create_coupon(self, discount_in_dollars, currency):
        discount_in_cents = int(discount_in_dollars * 100)

        try:
            stripe_coupon = stripe.Coupon.create(
                amount_off=discount_in_cents,
                duration='forever',
                currency=currency
            )

            return stripe_coupon
        except Exception as error:
            capture_message(f"Exception when calling stripe.Coupon.create with discount_in_dollars={discount_in_dollars}")
            capture_exception(error)
