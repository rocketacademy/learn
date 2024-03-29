from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse, HttpResponseRedirect
from django.test import Client, RequestFactory
from django.urls import reverse
import pytest

from payment.models.coupon_effect import CouponEffect
from staff.views.coupon_effect import DetailView

pytestmark = pytest.mark.django_db
client = Client()


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
def coupon_effect(course_factory):
    course = course_factory()
    coupon_effect = CouponEffect.objects.create(
        couponable_type=course.__class__.__name__,
        couponable_id=course.id,
        discount_type=CouponEffect.DOLLARS,
        discount_amount=10
    )

    yield coupon_effect

def test_anonymous_user_redirected_to_login(coupon_effect):
    request = RequestFactory().get(f"/coupon-effects/{coupon_effect.id}/")
    request.user = AnonymousUser()

    response = DetailView.as_view()(request, coupon_effect.id)

    assert response.status_code == HttpResponseRedirect.status_code
    assert f"staff/login/?next=/coupon-effects/{coupon_effect.id}/" in response.url

def test_template_rendered_for_logged_in_user(coupon_effect, logged_in_existing_user):
    response = client.get(
        reverse(
            'coupon_effect_detail',
            kwargs={'coupon_effect_id': coupon_effect.id}
        )
    )

    assert response.status_code == HttpResponse.status_code
    assert 'coupon_effect/detail.html' in (template.name for template in response.templates)
    assert response.context['coupon_effect'] == coupon_effect
