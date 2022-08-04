from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse, HttpResponseRedirect
from django.test import Client, RequestFactory
from django.urls import reverse
import pytest

from staff.forms.coupon_effect import CouponEffectForm
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

def test_anonymous_user_redirected_to_login():
    request = RequestFactory().get('/coupon-effects/new/')
    request.user = AnonymousUser()

    response = NewView.as_view()(request)

    assert response.status_code == HttpResponseRedirect.status_code
    assert 'staff/login/?next=/coupon-effects/new/' in response.url

def test_get_renders_with_form_when_user_logged_in(logged_in_existing_user):
    response = client.get(reverse('coupon_effect_new'))

    assert response.status_code == HttpResponse.status_code
    assert 'coupon_effect_form' in response.context
