import datetime
from django.utils.timezone import make_aware
import pytest

from payment.models.coupon import Coupon

pytestmark = pytest.mark.django_db


def test_coupon_create():
    start_date = make_aware(datetime.datetime.now())

    coupon = Coupon.objects.create(
        start_date=start_date,
        type='referral',
        discount_type='percent',
        discount_amount=10,
    )

    assert coupon.code is not None
    assert coupon.get_discount_display() == '10%'
