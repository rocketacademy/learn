import string
from django.conf import settings
import pytest

from payment.models.coupon_effect import CouponEffect
from staff.models import Course

pytestmark = pytest.mark.django_db


@pytest.fixture()
def course():
    course = Course.objects.create(name=settings.CODING_BASICS)

    yield course

def test_string_representation_when_couponable_exists(course):
    coupon_effect = CouponEffect.objects.create(
        couponable_type=course.__class__.__name__,
        couponable_id=course.id,
        discount_type=CouponEffect.DOLLARS,
        discount_amount=10
    )

    string_representation = coupon_effect.__str__()

    assert string_representation == '$10 off Coding Basics'

def test_string_representation_when_couponable_does_not_exist():
    coupon_effect = CouponEffect.objects.create(
        discount_type=CouponEffect.DOLLARS,
        discount_amount=10
    )

    string_representation = coupon_effect.__str__()

    assert string_representation == '$10 off'
