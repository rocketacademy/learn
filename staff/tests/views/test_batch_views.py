import datetime
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.test import Client, RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.urls import reverse
import pytest

from staff.models import Batch, Course
from staff.views import batches_view

pytestmark = pytest.mark.django_db
client = Client()

@pytest.fixture()
def existing_user():
    User = get_user_model()
    existing_user = User.objects.create_user(email='user@domain.com', first_name='FirstName', last_name='LastName', password='password1234!')

    return existing_user

@pytest.fixture()
def batch():
    COURSE_NAME = 'CODING_BASICS'
    COURSE_DURATION = 35

    start_date = datetime.date.today()
    end_date = start_date + datetime.timedelta(COURSE_DURATION)
    capacity = 90
    sections = 5

    course = Course.objects.create(name=COURSE_NAME)
    batch = Batch.objects.create(
        course=course,
        start_date=start_date,
        end_date=end_date,
        capacity=capacity,
        sections=sections
    )

    return batch

def test_batch_list_anonymous_user_redirected_to_login():
    request = RequestFactory().get('/coding-basics/batches/')
    request.user = AnonymousUser()

    response = batches_view(request)

    assert response.status_code == HttpResponseRedirect.status_code
    assert 'staff/login/?next=/coding-basics/batches/' in response.url

def test_batch_list_logged_in_user_can_access(existing_user):
    request = RequestFactory().get('/coding-basics/batches/')
    request.user = existing_user

    response = batches_view(request)

    assert response.status_code == HttpResponse.status_code

def test_batch_detail_template_rendered_if_batch_exists(batch, existing_user):
    client.post('/staff/login/', {'email': existing_user.email, 'password': 'password1234!'})

    response = client.get(reverse('batch_view', kwargs={'batch_id': batch.id}))

    assert response.status_code == HttpResponse.status_code
    assert 'coding_basics/batch/overview.html' in (template.name for template in response.templates)

def test_batch_detail_http_not_found_raised_if_batch_invalid(existing_user):
    invalid_batch_id = 1

    client.post('/staff/login/', {'email': existing_user.email, 'password': 'password1234!'})
    response = client.get(reverse('batch_view', kwargs={'batch_id': invalid_batch_id}))

    assert response.status_code == HttpResponseNotFound.status_code