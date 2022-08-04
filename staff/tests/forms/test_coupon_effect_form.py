from freezegun import freeze_time
import pytest

from staff.forms import CouponEffectForm

pytestmark = pytest.mark.django_db


def test_empty_form_is_invalid():
    coupon_effect_form = CouponEffectForm(data={})

    outcome = coupon_effect_form.is_valid()

    assert outcome is False

def test_discount_cannot_exceed_100_percent():
    coupon_effect_form = CouponEffectForm(
        data={
            'discount_amount': 101,
            'discount_type': 'percent'
        }
    )

    outcome = coupon_effect_form.is_valid()

    assert outcome is False
    assert 'Discount should not be more than 100%' in coupon_effect_form.errors['discount_amount']
    assert 'Discount should not be more than 100%' in coupon_effect_form.errors['discount_type']
