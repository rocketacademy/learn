from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect
from django.test import Client, RequestFactory
from django.urls import reverse
import pytest

from staff.views.batch import DetailView

pytestmark = pytest.mark.django_db
client = Client()


def test_anonymous_user_redirected_to_login(coding_basics_batch):
    request = RequestFactory().get(f"/courses/batches/{coding_basics_batch.id}/")
    request.user = AnonymousUser()

    response = DetailView.as_view()(request, coding_basics_batch.id)

    assert response.status_code == HttpResponseRedirect.status_code
    assert f"staff/login/?next=/courses/batches/{coding_basics_batch.id}/" in response.url

def test_redirect_to_coding_basics_batch_detail(coding_basics_batch, existing_user):
    client.post('/staff/login/', {'email': existing_user.email, 'password': settings.PLACEHOLDER_PASSWORD})

    response = client.get(reverse('batch_detail', kwargs={'batch_id': coding_basics_batch.id}))

    assert response.status_code == HttpResponseRedirect.status_code
    assert response['location'] == reverse('swe_fundamentals_batch_detail', kwargs={'batch_id': coding_basics_batch.id})

def test_redirect_to_swe_fundamentals_batch_detail(swe_fundamentals_batch, existing_user):
    client.post('/staff/login/', {'email': existing_user.email, 'password': settings.PLACEHOLDER_PASSWORD})

    response = client.get(reverse('batch_detail', kwargs={'batch_id': swe_fundamentals_batch.id}))

    assert response.status_code == HttpResponseRedirect.status_code
    assert response['location'] == reverse('swe_fundamentals_batch_detail', kwargs={'batch_id': swe_fundamentals_batch.id})

def test_redirect_to_bootcamp_batch_detail(coding_bootcamp_batch, existing_user):
    client.post('/staff/login/', {'email': existing_user.email, 'password': settings.PLACEHOLDER_PASSWORD})

    response = client.get(reverse('batch_detail', kwargs={'batch_id': coding_bootcamp_batch.id}))

    assert response.status_code == HttpResponseRedirect.status_code
    assert response['location'] == reverse('bootcamp_batch_detail', kwargs={'batch_id': coding_bootcamp_batch.id})
