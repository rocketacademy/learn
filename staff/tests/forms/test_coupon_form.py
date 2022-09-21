from datetime import date, timedelta
import pytest

from payment.models import CouponEffect
from staff.forms import CouponForm

pytestmark = pytest.mark.django_db


def test_empty_form_is_invalid():
    coupon_form = CouponForm(data={})

    outcome = coupon_form.is_valid()

    assert outcome is False

def test_start_date_cannot_be_after_end_date():
    coupon_effect = CouponEffect.objects.create(
        discount_type=CouponEffect.DOLLARS,
        discount_amount=10
    )
    coupon_form = CouponForm(
        data={
            'start_date': date.today(),
            'end_date': date.today() - timedelta(days=1),
            'effects': [coupon_effect]
        }
    )

    outcome = coupon_form.is_valid()

    assert outcome is False
    assert 'Start date must be before end date' in coupon_form.errors['start_date']
    assert 'Start date must be before end date' in coupon_form.errors['end_date']
