from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.test import Client, RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
import pytest

from staff.views.basics.basics_registration import ListView

pytestmark = pytest.mark.django_db
client = Client()


def test_batch_registration_list_anonymous_user_redirected_to_login(coding_basics_batch):
    request = RequestFactory().get(f"/swe-fundamentals/batches/{coding_basics_batch.id}/registrations/")
    request.user = AnonymousUser()

    response = ListView.as_view()(request)

    assert response.status_code == HttpResponseRedirect.status_code
    assert f"staff/login/?next=/swe-fundamentals/batches/{coding_basics_batch.id}/registrations/" in response.url

def test_coding_basics_batch_registration_list_contains_registrations(coding_basics_registration, existing_user):
    batch = coding_basics_registration.batch
    client.post('/staff/login/', {'email': existing_user.email, 'password': settings.PLACEHOLDER_PASSWORD})

    response = client.get(reverse('swe_fundamentals_batch_registration_list', kwargs={'batch_id': batch.id}))

    assert response.status_code == HttpResponse.status_code
    assert list(response.context['registrations']) == [coding_basics_registration]
    assert 'basics/registration/list.html' in (template.name for template in response.templates)

def test_swe_fundamentals_batch_registration_list_contains_registrations(swe_fundamentals_registration, existing_user):
    batch = swe_fundamentals_registration.batch
    client.post('/staff/login/', {'email': existing_user.email, 'password': settings.PLACEHOLDER_PASSWORD})

    response = client.get(reverse('swe_fundamentals_batch_registration_list', kwargs={'batch_id': batch.id}))

    assert response.status_code == HttpResponse.status_code
    assert list(response.context['registrations']) == [swe_fundamentals_registration]
    assert 'basics/registration/list.html' in (template.name for template in response.templates)
