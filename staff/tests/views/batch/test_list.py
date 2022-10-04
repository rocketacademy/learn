import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.test import RequestFactory
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
import pytest

from staff.models import Batch, Course
from staff.views.batch import ListView

pytestmark = pytest.mark.django_db

@pytest.fixture()
def existing_user():
    User = get_user_model()
    existing_user = User.objects.create_user(
        email='user@domain.com',
        first_name='FirstName',
        last_name='LastName',
        password='password1234!'
    )

    yield existing_user

@pytest.fixture()
def batch():
    COURSE_NAME = Course.CODING_BASICS
    COURSE_DURATION_IN_DAYS = 35

    start_date = datetime.date.today()
    course = Course.objects.create(name=COURSE_NAME)
    batch = Batch.objects.create(
        course=course,
        start_date=start_date,
        end_date=start_date + datetime.timedelta(COURSE_DURATION_IN_DAYS),
        capacity=90,
        sections=5
    )

    yield batch

def test_anonymous_user_redirected_to_login():
    request = RequestFactory().get('/basics/batches/')
    request.user = AnonymousUser()

    response = ListView.as_view()(request)

    assert response.status_code == HttpResponseRedirect.status_code
    assert 'staff/login/?next=/basics/batches/' in response.url

def test_logged_in_user_can_access(existing_user):
    request = RequestFactory().get('/basics/batches/')
    request.user = existing_user

    response = ListView.as_view()(request)

    assert response.status_code == HttpResponse.status_code
