from django.http import HttpResponse, HttpResponseRedirect
from django.test import Client, RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.urls import reverse
import pytest

from staff.views.registration import ListView

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

def test_registration_list_anonymous_user_redirected_to_login(batch_factory):
    batch = batch_factory()
    request = RequestFactory().get(f"/basics/batches/{batch.id}/registrations/")
    request.user = AnonymousUser()

    response = ListView.as_view()(request)

    assert response.status_code == HttpResponseRedirect.status_code
    assert f"staff/login/?next=/basics/batches/{batch.id}/registrations/" in response.url

def test_registration_list_logged_in_user_can_access(batch_factory, logged_in_existing_user):
    batch = batch_factory()

    response = client.get(reverse('registration_list', kwargs={'batch_id': batch.id}))

    assert response.status_code == HttpResponse.status_code
    assert 'basics/registration/list.html' in (template.name for template in response.templates)
