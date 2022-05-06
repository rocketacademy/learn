import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.test import Client, RequestFactory
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.urls import reverse
from freezegun import freeze_time
import pytest

from staff.models import Batch, Course, Section
from staff.views.batch import edit

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

@pytest.fixture()
def section(batch):
    section = Section.objects.create(
        batch=batch,
        number=1,
        capacity=18
    )

    yield section

def test_anonymous_user_redirected_to_login(batch):
    request = RequestFactory().get(f"/basics/batches/{batch.id}/edit/")
    request.user = AnonymousUser()

    response = edit(request, batch.id)

    assert response.status_code == HttpResponseRedirect.status_code
    assert f"staff/login/?next=/basics/batches/{batch.id}/edit" in response.url

def test_logged_in_user_can_access(batch, section, existing_user):
    request = RequestFactory().get(f"/basics/batches/{batch.id}/edit/")
    request.user = existing_user

    response = edit(request, batch.id)

    assert response.status_code == HttpResponse.status_code

def test_template_rendered_if_batch_exists(batch, section, existing_user):
    client.post('/staff/login/', {'email': existing_user.email, 'password': 'password1234!'})

    response = client.get(reverse('batch_edit', kwargs={'batch_id': batch.id}))

    assert response.status_code == HttpResponse.status_code
    assert 'basics/batch/edit.html' in (template.name for template in response.templates)

def test_template_rendered_again_if_sections_incorrectly_reduced(batch, section, existing_user):
    incorrectly_reduced_number_of_sections = 0
    payload = {
        'start_date': '2022-01-01',
        'end_date': '2022-02-01',
        'sections': incorrectly_reduced_number_of_sections,
        'capacity': section.capacity
    }
    client.post('/staff/login/', {
        'email': existing_user.email,
        'password': 'password1234!'}
    )

    freezer = freeze_time('2021-12-31')
    freezer.start()
    response = client.post(reverse('batch_edit', kwargs={'batch_id': batch.id}), data=payload)
    freezer.stop()

    assert response.status_code == HttpResponse.status_code
    assert 'basics/batch/edit.html' in (template.name for template in response.templates)

def test_template_rendered_again_if_section_capacity_incorrectly_reduced(batch, section, existing_user):
    incorrectly_reduced_section_capacity = section.capacity - 1
    payload = {
        'start_date': '2022-01-01',
        'end_date': '2022-02-01',
        'sections': Section.objects.all().count(),
        'capacity': incorrectly_reduced_section_capacity
    }
    client.post('/staff/login/', {
        'email': existing_user.email,
        'password': 'password1234!'}
    )

    freezer = freeze_time('2021-12-31')
    freezer.start()
    response = client.post(reverse('batch_edit', kwargs={'batch_id': batch.id}), data=payload)
    freezer.stop()

    assert response.status_code == HttpResponse.status_code
    assert 'basics/batch/edit.html' in (template.name for template in response.templates)

def test_valid_form_updates_and_creates_records(batch, section, existing_user):
    new_start_date = batch.start_date + datetime.timedelta(1)
    new_end_date = batch.end_date + datetime.timedelta(1)
    number_of_sections = Section.objects.all().count() + 1
    section_capacity = section.capacity + 1
    payload = {
        'start_date': new_start_date,
        'end_date': new_end_date,
        'sections': number_of_sections,
        'capacity': section_capacity,
    }
    client.post('/staff/login/', {
        'email': existing_user.email,
        'password': 'password1234!'}
    )

    freezer = freeze_time('2021-12-31')
    freezer.start()
    response = client.post(reverse('batch_edit', kwargs={'batch_id': batch.id}), data=payload)
    freezer.stop()

    assert response.status_code == HttpResponseRedirect.status_code
    assert response['Location'] == reverse('batch_detail', kwargs={'batch_id': batch.id})

    batch = Batch.objects.first()
    assert batch.start_date == new_start_date
    assert batch.end_date == new_end_date
    assert batch.sections == number_of_sections
    assert batch.capacity == number_of_sections * section_capacity

    section_queryset = Section.objects.all()
    assert section_queryset.count() == number_of_sections
    assert section_queryset.first().capacity == section_capacity
