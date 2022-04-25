import datetime
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.test import Client, RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.urls import reverse
import pytest

from staff.models import Batch, Course, Section
from staff.views import sections_view

pytestmark = pytest.mark.django_db
client = Client()

@pytest.fixture()
def logged_in_existing_user():
    User = get_user_model()
    existing_user = User.objects.create_user(email='user@domain.com', first_name='FirstName', last_name='LastName', password='password1234!')
    client.post('/staff/login/', {'email': existing_user.email, 'password': 'password1234!'})

    yield logged_in_existing_user

@pytest.fixture()
def batch():
    COURSE_NAME = 'CODING_BASICS'
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

@pytest.fixture()
def sections(batch):
    SECTION_CAPACITY = 18

    Section.objects.create(
        batch=batch,
        number=1,
        capacity=SECTION_CAPACITY
    )
    Section.objects.create(
        batch=batch,
        number=2,
        capacity=SECTION_CAPACITY
    )

    sections_queryset = Section.objects.filter(batch__id=batch.id)

    yield sections_queryset

def test_section_list_anonymous_user_redirected_to_login(sections):
    batch = sections.first().batch
    request = RequestFactory().get(f"/coding-basics/batches/{batch.id}/sections/")
    request.user = AnonymousUser()

    response = sections_view(request)

    assert response.status_code == HttpResponseRedirect.status_code
    assert f"staff/login/?next=/coding-basics/batches/{batch.id}/sections/" in response.url

def test_section_list_logged_in_user_can_access(sections, logged_in_existing_user):
    batch = sections.first().batch

    response = client.get(reverse('sections_view', kwargs={'batch_id': batch.id}))

    assert response.status_code == HttpResponse.status_code
    assert 'coding_basics/batch/sections.html' in (template.name for template in response.templates)

def test_section_list_http_not_found_if_batch_invalid(logged_in_existing_user):
    invalid_batch_id = 1

    response = client.get(reverse('sections_view', kwargs={'batch_id': invalid_batch_id}))

    assert response.status_code == HttpResponseNotFound.status_code

def test_section_detail_template_rendered_if_batch_and_sections_exists(sections, logged_in_existing_user):
    section_one = sections.first()
    batch = section_one.batch

    response = client.get(reverse('section_view', kwargs={'batch_id': batch.id, 'section_id': section_one.id}))

    assert response.status_code == HttpResponse.status_code
    assert 'coding_basics/section/overview.html' in (template.name for template in response.templates)

def test_section_detail_http_not_found_raised_if_batch_invalid(sections, logged_in_existing_user):
    invalid_batch_id = 0
    section_one = sections.first()

    response = client.get(reverse('section_view', kwargs={'batch_id': invalid_batch_id, 'section_id': section_one.id}))

    assert response.status_code == HttpResponseNotFound.status_code

def test_section_detail_http_not_found_raised_if_section_invalid(batch, logged_in_existing_user):
    invalid_section_id = 0

    response = client.get(reverse('section_view', kwargs={'batch_id': batch.id, 'section_id': invalid_section_id}))

    assert response.status_code == HttpResponseNotFound.status_code