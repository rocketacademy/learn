import pytest

from payment.models.coupon_effect import CouponEffect
from staff.models import Course

pytestmark = pytest.mark.django_db


def test_string_representation_when_couponable_exists(course_factory):
    swe_fundamentals_course = course_factory(swe_fundamentals=True)
    coupon_effect = CouponEffect.objects.create(
        couponable_type=swe_fundamentals_course.__class__.__name__,
        couponable_id=swe_fundamentals_course.id,
        discount_type=CouponEffect.DOLLARS,
        discount_amount=10
    )

    string_representation = coupon_effect.__str__()

    assert string_representation == '$10 off Software Engineering Fundamentals'

def test_string_representation_when_couponable_does_not_exist():
    coupon_effect = CouponEffect.objects.create(
        discount_type=CouponEffect.DOLLARS,
        discount_amount=10
    )

    string_representation = coupon_effect.__str__()

    assert string_representation == '$10 off'
