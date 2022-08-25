import datetime
from django.conf import settings
from django.utils.timezone import make_aware
import pytest

from payment.models.coupon import Coupon
from payment.models.coupon_effect import CouponEffect
from staff.models import Course

pytestmark = pytest.mark.django_db


@pytest.fixture()
def coupon_effect():
    course = Course.objects.create(name=settings.CODING_BASICS)
    coupon_effect = CouponEffect.objects.create(
        couponable_type=course.__class__.__name__,
        couponable_id=course.id,
        discount_type='dollars',
        discount_amount=10
    )

    yield coupon_effect

def test_coupon_create(coupon_effect):
    coupon = Coupon.objects.create(start_date=make_aware(datetime.datetime.now()))
    coupon.effects.set([coupon_effect])

    assert coupon.code is not None
    assert coupon.effects.first() == coupon_effect

def test_custom_coupon_code_saved(coupon_effect):
    custom_code = 'CUSTOMCODE'

    coupon = Coupon.objects.create(
        code=custom_code,
        start_date=make_aware(datetime.datetime.now())
    )
    coupon.effects.set([coupon_effect])

    assert coupon.code == custom_code

def test_custom_coupon_code_not_saved_if_already_exists(coupon_effect):
    custom_code = 'CUSTOMCODE'
    existing_coupon = Coupon.objects.create(
        code=custom_code,
        start_date=make_aware(datetime.datetime.now())
    )

    with pytest.raises(ValueError) as exception_info:
        Coupon.objects.create(
            code=custom_code,
            start_date=make_aware(datetime.datetime.now())
        )

    assert str(exception_info.value) == 'Coupon with specified code already exists'

def test_new_code_generated_if_code_already_exists(coupon_effect):
    existing_coupon = Coupon.objects.create(start_date=make_aware(datetime.datetime.now()))
    existing_code = existing_coupon.code

    with pytest.raises(ValueError) as exception_info:
        Coupon.objects.create(
            code=existing_code,
            start_date=make_aware(datetime.datetime.now())
        )

    assert str(exception_info.value) == 'Coupon with specified code already exists'

def test_get_effects_display():
    first_coupon_effect = CouponEffect.objects.create(
        discount_type='dollars',
        discount_amount=10
    )
    second_coupon_effect = CouponEffect.objects.create(
        discount_type='dollars',
        discount_amount=20
    )

    coupon = Coupon.objects.create(start_date=make_aware(datetime.datetime.now()))
    coupon.effects.set([first_coupon_effect, second_coupon_effect])

    html_formatted_coupon_effects = coupon.get_effects_display()

    assert html_formatted_coupon_effects == "$10 off<br>$20 off<br>"

def test_biggest_discount_for_coding_basics():
    coding_basics_course = Course.objects.create(name=settings.CODING_BASICS)
    discount_for_coding_basics_1 = CouponEffect.objects.create(
        couponable_type=type(coding_basics_course).__name__,
        couponable_id=coding_basics_course.id,
        discount_type='dollars',
        discount_amount=10
    )
    discount_for_coding_basics_2 = CouponEffect.objects.create(
        couponable_type=type(coding_basics_course).__name__,
        couponable_id=coding_basics_course.id,
        discount_type='dollars',
        discount_amount=20
    )
    biggest_discount_for_coding_basics = CouponEffect.objects.create(
        couponable_type=type(coding_basics_course).__name__,
        couponable_id=coding_basics_course.id,
        discount_type='percent',
        discount_amount=20
    )
    coupon = Coupon.objects.create(start_date=make_aware(datetime.datetime.now()))
    coupon.effects.set([discount_for_coding_basics_1, discount_for_coding_basics_2, biggest_discount_for_coding_basics])

    result = coupon.biggest_discount_for(coding_basics_course, settings.CODING_BASICS_REGISTRATION_FEE_SGD)

    biggest_discount = round((biggest_discount_for_coding_basics.discount_amount / 100 * settings.CODING_BASICS_REGISTRATION_FEE_SGD), 2)
    assert result == biggest_discount
