from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse, HttpResponseRedirect
from django.test import Client, RequestFactory
from django.urls import reverse
import pytest

from staff.views.bootcamp.bootcamp_batch import ListView

client = Client()
pytestmark = pytest.mark.django_db

def test_anonymous_user_redirected_to_login():
    request = RequestFactory().get('/bootcamp/batches/')
    request.user = AnonymousUser()

    response = ListView.as_view()(request)

    assert response.status_code == HttpResponseRedirect.status_code
    assert 'staff/login/?next=/bootcamp/batches/' in response.url

def test_bootcamp_batches_displayed_to_logged_in_user(existing_user, coding_bootcamp_batch):
    client.post('/staff/login/', {'email': existing_user.email, 'password': settings.PLACEHOLDER_PASSWORD})

    response = client.get(reverse('bootcamp_batch_list'))

    assert response.status_code == HttpResponse.status_code
    assert list(response.context['batches']) == [coding_bootcamp_batch]
