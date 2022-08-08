from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse, HttpResponseRedirect
from django.test import Client, RequestFactory
from django.urls import reverse
import pytest

from payment.models.coupon_effect import CouponEffect
from payment.models.stripe_coupon_effect import StripeCouponEffect
from staff.models import Course
from staff.views.coupon_effect import NewView

pytestmark = pytest.mark.django_db
client = Client()
User = get_user_model()

existing_user_email = 'existing_user@email.com'
existing_user_first_name = 'Existing'
existing_user_last_name = 'User'
existing_user_password = settings.PLACEHOLDER_PASSWORD

@pytest.fixture()
def logged_in_existing_user():
    User = get_user_model()
    existing_user = User.objects.create_user(
        email='user@domain.com',
        first_name='FirstName',
        last_name='LastName',
        password='password1234!'
    )
    client.post('/staff/login/', {'email': existing_user.email, 'password': 'password1234!'})

    yield logged_in_existing_user

@pytest.fixture()
def course():
    course = Course.objects.create(name=settings.CODING_BASICS)

    yield course

def test_anonymous_user_redirected_to_login():
    request = RequestFactory().get('/coupon-effects/new/')
    request.user = AnonymousUser()

    response = NewView.as_view()(request)

    assert response.status_code == HttpResponseRedirect.status_code
    assert 'staff/login/?next=/coupon-effects/new/' in response.url

def test_get_renders_with_form_when_user_logged_in(logged_in_existing_user):
    response = client.get(reverse('coupon_effect_new'))

    assert response.status_code == HttpResponse.status_code
    assert 'coupon_effect/new.html' in (template.name for template in response.templates)
    assert 'stripe_coupon_effect_form' in response.context

def test_post_stores_stripe_coupon_id_in_stripe_coupon_effect(course, logged_in_existing_user, mocker):
    stripe_coupon_id = 'Z4OV52SU'
    mocker.patch(
        'staff.views.coupon_effect.create_stripe_coupon',
        return_value={
            "id": "Z4OV52SU",
            "object": "coupon",
            "amount_off": None,
            "created": 1659930573,
            "currency": "sgd",
            "duration": "repeating",
            "duration_in_months": 3,
            "livemode": False,
            "max_redemptions": None,
            "metadata": {},
            "name": "15% off",
            "percent_off": 15,
            "redeem_by": None,
            "times_redeemed": 0,
            "valid": True
        }
    )

    client.post(
        reverse('coupon_effect_new'),
        {
            'discount_amount': 15,
            'discount_type': 'percent',
        }
    )

    stripe_coupon_effect = StripeCouponEffect.objects.first()
    assert stripe_coupon_effect.stripe_coupon_id == stripe_coupon_id

def test_post_saves_form_with_coding_basics_as_couponable(course, logged_in_existing_user):
    response = client.post(
        reverse('coupon_effect_new'),
        {
            'discount_amount': 15,
            'discount_type': 'percent',
        }
    )

    coupon_effect = CouponEffect.objects.first()
    assert response.status_code == HttpResponseRedirect.status_code
    assert f"staff/coupon-effects/{coupon_effect.id}/" in response.url
    assert coupon_effect.couponable_type == type(course).__name__
    assert coupon_effect.couponable_id == course.id
    assert coupon_effect.discount_amount == 15
    assert coupon_effect.discount_type == 'percent'
