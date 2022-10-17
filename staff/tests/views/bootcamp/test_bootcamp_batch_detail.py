from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse, HttpResponseRedirect
from django.test import Client, RequestFactory
from django.urls import reverse
import pytest

from staff.views.bootcamp.bootcamp_batch import DetailView

pytestmark = pytest.mark.django_db
client = Client()


def test_anonymous_user_redirected_to_login(coding_bootcamp_batch):
    request = RequestFactory().get(f"/bootcamp/batches/{coding_bootcamp_batch.id}/")
    request.user = AnonymousUser()

    response = DetailView.as_view()(request, coding_bootcamp_batch.id)

    assert response.status_code == HttpResponseRedirect.status_code
    assert f"staff/login/?next=/bootcamp/batches/{coding_bootcamp_batch.id}/" in response.url

def test_logged_in_user_can_access(coding_bootcamp_batch, existing_user):
    request = RequestFactory().get(f"/bootcamp/batches/{coding_bootcamp_batch.id}/")
    request.user = existing_user

    response = DetailView.as_view()(request, coding_bootcamp_batch.id)

    assert response.status_code == HttpResponse.status_code

def test_template_rendered_if_batch_exists(coding_bootcamp_batch, existing_user):
    client.post('/staff/login/', {'email': existing_user.email, 'password': settings.PLACEHOLDER_PASSWORD})

    response = client.get(reverse('bootcamp_batch_detail', kwargs={'batch_id': coding_bootcamp_batch.id}))

    assert response.status_code == HttpResponse.status_code
    assert 'bootcamp/batch/detail.html' in (template.name for template in response.templates)
