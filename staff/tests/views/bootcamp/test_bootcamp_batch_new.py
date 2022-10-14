from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse, HttpResponseRedirect
from django.test import Client, RequestFactory
import pytest

from staff.views.bootcamp.bootcamp_batch import NewView

pytestmark = pytest.mark.django_db
client = Client()


def test_anonymous_user_redirected_to_login(course_factory):
    coding_bootcamp_course = course_factory(coding_bootcamp=True)
    request = RequestFactory().get('/bootcamp/batches/new/')
    request.user = AnonymousUser()

    response = NewView.as_view()(request)

    assert response.status_code == HttpResponseRedirect.status_code
    assert 'staff/login/?next=/bootcamp/batches/' in response.url

def test_logged_in_user_can_access(course_factory, user_factory):
    coding_bootcamp_course = course_factory(coding_bootcamp=True)
    existing_user = user_factory()
    request = RequestFactory().get('/bootcamp/batches/new/')
    request.user = existing_user
    form_id = 'create-batch-form'

    response = NewView.as_view()(request)

    assert response.status_code == HttpResponse.status_code
    assert form_id in str(response.content)
