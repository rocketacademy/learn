import pytest
from django.utils.timezone import now, timedelta
from django.conf import settings

from payment.models.coupon import Coupon
from payment.models.coupon_effect import CouponEffect
from staff.models import Course
from student.forms import StudentInfoForm

pytestmark = pytest.mark.django_db


def test_validation_error_shows_when_referral_code_does_not_exist():
    course = Course.objects.create(name=Course.CODING_BASICS)
    coupon_effect = CouponEffect.objects.create(
        couponable_type=type(course).__name__,
        couponable_id=course.id,
        discount_type=CouponEffect.DOLLARS,
        discount_amount=10
    )
    coupon = Coupon.objects.create(
        start_date=now(),
        end_date=now() + timedelta(days=1),
    )
    coupon.effects.set([coupon_effect])
    student_info_form = StudentInfoForm(
        data={
            'first_name': 'Student',
            'last_name': 'User',
            'email': 'student@example.com',
            'country_of_residence': 'SG',
            'referral_channel': 'word_of_mouth',
            'referral_code': 'invalid_code'
        }
    )

    outcome = student_info_form.is_valid()

    assert outcome is False
    assert 'Referral code is invalid' in student_info_form.errors['referral_code']


def test_validation_error_shows_when_referral_code_premature():
    course = Course.objects.create(name=Course.CODING_BASICS)
    coupon_effect = CouponEffect.objects.create(
        couponable_type=type(course).__name__,
        couponable_id=course.id,
        discount_type=CouponEffect.DOLLARS,
        discount_amount=10
    )
    coupon = Coupon.objects.create(start_date=now() + timedelta(days=1))
    coupon.effects.set([coupon_effect])
    student_info_form = StudentInfoForm(
        data={
            'first_name': 'Student',
            'last_name': 'User',
            'email': 'student@example.com',
            'country_of_residence': 'SG',
            'referral_channel': 'word_of_mouth',
            'referral_code': coupon.code
        }
    )

    outcome = student_info_form.is_valid()

    assert outcome is False
    assert 'Referral code is not in effect yet' in student_info_form.errors['referral_code']


def test_validation_error_shows_when_referral_code_expired():
    course = Course.objects.create(name=Course.CODING_BASICS)
    coupon_effect = CouponEffect.objects.create(
        couponable_type=type(course).__name__,
        couponable_id=course.id,
        discount_type=CouponEffect.DOLLARS,
        discount_amount=10
    )
    coupon = Coupon.objects.create(
        start_date=now() - timedelta(days=2),
        end_date=now() - timedelta(days=1),
    )
    coupon.effects.set([coupon_effect])
    student_info_form = StudentInfoForm(
        data={
            'first_name': 'Student',
            'last_name': 'User',
            'email': 'student@example.com',
            'country_of_residence': 'SG',
            'referral_channel': 'word_of_mouth',
            'referral_code': coupon.code
        }
    )

    outcome = student_info_form.is_valid()

    assert outcome is False
    assert 'Referral code has expired' in student_info_form.errors['referral_code']
