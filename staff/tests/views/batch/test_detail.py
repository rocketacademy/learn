import datetime
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseRedirect
from django.test import Client, RequestFactory
from django.urls import reverse
import pytest

from staff.models import Batch, Course, Section
from staff.views.batch import DetailView

pytestmark = pytest.mark.django_db
client = Client()

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

@pytest.fixture()
def section(batch):
    section = Section.objects.create(
        batch=batch,
        number=1,
        capacity=18
    )

    yield section

def test_anonymous_user_redirected_to_login(batch):
    request = RequestFactory().get(f"/basics/batches/{batch.id}/")
    request.user = AnonymousUser()

    response = DetailView.as_view()(request, batch.id)

    assert response.status_code == HttpResponseRedirect.status_code
    assert f"staff/login/?next=/basics/batches/{batch.id}/" in response.url

def test_logged_in_user_can_access(batch, section, existing_user):
    request = RequestFactory().get(f"/basics/batches/{batch.id}/")
    request.user = existing_user

    response = DetailView.as_view()(request, batch.id)

    assert response.status_code == HttpResponse.status_code

def test_template_rendered_if_batch_exists(batch, section, existing_user):
    client.post('/staff/login/', {'email': existing_user.email, 'password': 'password1234!'})

    response = client.get(reverse('batch_detail', kwargs={'batch_id': batch.id}))

    assert response.status_code == HttpResponse.status_code
    assert 'basics/batch/detail.html' in (template.name for template in response.templates)
