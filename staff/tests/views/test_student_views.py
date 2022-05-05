import datetime
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.test import Client, RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.urls import reverse
import pytest

from staff.models import Batch, Course
from staff.views.student import list

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

@pytest.fixture()
def batch():
    COURSE_NAME = settings.CODING_BASICS
    COURSE_DURATION = 35

    start_date = datetime.date.today()
    course = Course.objects.create(name=COURSE_NAME)
    batch = Batch.objects.create(
        course=course,
        start_date=start_date,
        end_date=start_date + datetime.timedelta(COURSE_DURATION),
        capacity=90,
        sections=5
    )

    yield batch

def test_student_list_anonymous_user_redirected_to_login(batch):
    request = RequestFactory().get(f"/basics/batches/{batch.id}/students/")
    request.user = AnonymousUser()

    response = list(request)

    assert response.status_code == HttpResponseRedirect.status_code
    assert f"staff/login/?next=/basics/batches/{batch.id}/students/" in response.url

def test_student_list_logged_in_user_can_access(batch, logged_in_existing_user):
    response = client.get(reverse('student_list', kwargs={'batch_id': batch.id}))

    assert response.status_code == HttpResponse.status_code
    assert 'basics/student/list.html' in (template.name for template in response.templates)
