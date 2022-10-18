from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse, HttpResponseRedirect
from django.test import RequestFactory
import pytest

from staff.views.batch import ListView

pytestmark = pytest.mark.django_db

def test_anonymous_user_redirected_to_login():
    request = RequestFactory().get('/courses/batches/')
    request.user = AnonymousUser()

    response = ListView.as_view()(request)

    assert response.status_code == HttpResponseRedirect.status_code
    assert 'staff/login/?next=/courses/batches/' in response.url

def test_logged_in_user_can_access(coding_basics_batch, coding_bootcamp_batch, existing_user):
    request = RequestFactory().get('/courses/batches/')
    request.user = existing_user

    response = ListView.as_view()(request)

    assert response.status_code == HttpResponse.status_code
