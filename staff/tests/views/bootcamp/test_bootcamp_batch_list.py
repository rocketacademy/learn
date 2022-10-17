from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse, HttpResponseRedirect
from django.test import RequestFactory
import pytest

from staff.views.bootcamp.bootcamp_batch import ListView

pytestmark = pytest.mark.django_db

def test_anonymous_user_redirected_to_login():
    request = RequestFactory().get('/basics/batches/')
    request.user = AnonymousUser()

    response = ListView.as_view()(request)

    assert response.status_code == HttpResponseRedirect.status_code
    assert 'staff/login/?next=/basics/batches/' in response.url

def test_logged_in_user_can_access(user_factory, batch_factory, course_factory):
    coding_bootcamp_course = course_factory(coding_bootcamp=True)
    coding_bootcamp_batch = batch_factory(course=coding_bootcamp_course)
    existing_user = user_factory()
    request = RequestFactory().get('/bootcamp/batches/')
    request.user = existing_user

    response = ListView.as_view()(request)

    assert response.status_code == HttpResponse.status_code
