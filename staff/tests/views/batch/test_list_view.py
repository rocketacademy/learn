from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect
from django.test import Client, RequestFactory
from django.urls import reverse
import pytest

from staff.views.batch import ListView

client = Client()
pytestmark = pytest.mark.django_db

def test_anonymous_user_redirected_to_login():
    request = RequestFactory().get('/batches/')
    request.user = AnonymousUser()

    response = ListView.as_view()(request)

    assert response.status_code == HttpResponseRedirect.status_code
    assert 'staff/login/?next=/batches/' in response.url

def test_different_course_batches_displayed(existing_user, batch_factory):
    swe_fundamentals_batch = batch_factory(swe_fundamentals=True)
    coding_basics_batch = batch_factory(coding_basics=True)
    coding_bootcamp_batch = batch_factory(coding_bootcamp=True)
    client.post('/staff/login/', {'email': existing_user.email, 'password': settings.PLACEHOLDER_PASSWORD})

    response = client.get(reverse('batch_list'))

    assert list(response.context['batches']) == [swe_fundamentals_batch, coding_basics_batch, coding_bootcamp_batch]
