from datetime import datetime
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse, HttpResponseRedirect
from django.test import Client, RequestFactory
from django.urls import reverse
from django.utils.timezone import make_aware
import pytest

from payment.models.coupon import Coupon
from payment.models.coupon_effect import CouponEffect
from staff.views.coupon import DetailView

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
def coupon(course_factory):
    coding_basics_course = course_factory()
    coupon_effect = CouponEffect.objects.create(
        couponable_type=coding_basics_course.__class__.__name__,
        couponable_id=coding_basics_course.id,
        discount_type=CouponEffect.DOLLARS,
        discount_amount=10
    )
    coupon = Coupon.objects.create(
        start_date=make_aware(datetime.now()),
        end_date=None,
        description='Some description'
    )
    coupon.effects.set([coupon_effect])

    yield coupon

def test_coupon_detail_anonymous_user_redirected_to_login(coupon):
    request = RequestFactory().get(f"/coupons/{coupon.id}/")
    request.user = AnonymousUser()

    response = DetailView.as_view()(request, coupon.id)

    assert response.status_code == HttpResponseRedirect.status_code
    assert f"staff/login/?next=/coupons/{coupon.id}/" in response.url

def test_coupon_detail_template_rendered_for_logged_in_user(coupon, logged_in_existing_user):
    response = client.get(reverse('coupon_detail', kwargs={'coupon_id': coupon.id}))

    assert response.status_code == HttpResponse.status_code
    assert 'coupon/detail.html' in (template.name for template in response.templates)
