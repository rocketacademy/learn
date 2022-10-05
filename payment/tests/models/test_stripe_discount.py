from django.conf import settings
import pytest

from payment.models.stripe_discount import StripeDiscount
from payment.models.stripe_payment import StripePayment

pytestmark = pytest.mark.django_db

DISCOUNT_AMOUNT_IN_DOLLARS = 20

@pytest.fixture()
def stripe_discount():
    stripe_discount = StripeDiscount.objects.create(
        amount=DISCOUNT_AMOUNT_IN_DOLLARS * settings.CENTS_PER_DOLLAR,
        coupon_id=1
    )

    yield stripe_discount

def test_dollar_amount(stripe_discount):
    discount_dollar_amount = stripe_discount.dollar_amount()

    assert discount_dollar_amount == DISCOUNT_AMOUNT_IN_DOLLARS
