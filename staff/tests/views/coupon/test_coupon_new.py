from datetime import datetime
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse, HttpResponseRedirect
from django.test import Client, RequestFactory
from django.urls import reverse
from django.utils.timezone import make_aware
import pytest

from payment.models import Coupon
from payment.models import CouponEffect
from staff.views.coupon import NewView

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

def test_coupon_new_anonymous_user_redirected_to_login():
    request = RequestFactory().get('/coupons/new/')
    request.user = AnonymousUser()

    response = NewView.as_view()(request)

    assert response.status_code == HttpResponseRedirect.status_code
    assert 'staff/login/?next=/coupons/new/' in response.url

def test_coupon_new_template_rendered_for_logged_in_user(logged_in_existing_user):
    response = client.get(reverse('coupon_new'))

    assert response.status_code == HttpResponse.status_code
    assert 'coupon/new.html' in (template.name for template in response.templates)

def test_coupon_not_created_if_coupon_with_code_exists(logged_in_existing_user):
    existing_coupon = Coupon.objects.create(start_date=make_aware(datetime.today()))
    coupon_effect = CouponEffect.objects.create(
        discount_type=CouponEffect.DOLLARS,
        discount_amount=10
    )

    response = client.post(
        reverse('coupon_new'),
        {
            'start_date': make_aware(datetime.today()),
            'code': existing_coupon.code,
            'effects': [coupon_effect.id]
        }
    )

    assert f"Coupon with code {existing_coupon.code} already exists" in response.context['coupon_form'].errors['code']
