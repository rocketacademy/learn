from django.conf import settings
import pytest

from payment.models.stripe_payment import StripePayment

pytestmark = pytest.mark.django_db


@pytest.fixture()
def stripe_payment():
    stripe_payment = StripePayment.objects.create(
        payable_type='Registration',
        payable_id=1,
        intent='pi_3L65dXHQt5htmvv4176vtmCj',
        customer='cus_Lnh1zdmxckmUUU',
        customer_email='customer_email@example.com',
        amount=settings.SWE_FUNDAMENTALS_REGISTRATION_FEE_SGD * settings.CENTS_PER_DOLLAR,
        currency=settings.SINGAPORE_DOLLAR_CURRENCY,
        status='paid'
    )

    yield stripe_payment

def test_dollar_amount(stripe_payment):
    dollar_amount = stripe_payment.dollar_amount()

    assert dollar_amount == settings.SWE_FUNDAMENTALS_REGISTRATION_FEE_SGD
