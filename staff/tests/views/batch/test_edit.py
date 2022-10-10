from datetime import date, time, timedelta
from django.http import HttpResponse, HttpResponseRedirect
from django.test import Client, RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.urls import reverse
from freezegun import freeze_time
import pytest

from staff.models import Batch, Section
from staff.models.batch_schedule import BatchSchedule
from staff.views.batch import EditView
from student.library.slack import Slack

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
def batch_with_section_and_batch_schedule(batch_factory):
    batch = batch_factory(start_date=date(2022, 1, 7))
    Section.objects.create(
        batch=batch,
        number=1,
        capacity=18
    )
    BatchSchedule.objects.create(
        batch=batch,
        day='MON',
        iso_week_day='1',
        start_time='00:00:00',
        end_time='02:00:00',
    )

    yield batch

def test_anonymous_user_redirected_to_login(batch_with_section_and_batch_schedule):
    request = RequestFactory().get(f"/basics/batches/{batch_with_section_and_batch_schedule.id}/edit/")
    request.user = AnonymousUser()

    response = EditView.as_view()(request, batch_with_section_and_batch_schedule.id)

    assert response.status_code == HttpResponseRedirect.status_code
    assert f"staff/login/?next=/basics/batches/{batch_with_section_and_batch_schedule.id}/edit" in response.url

def test_logged_in_user_can_access(batch_with_section_and_batch_schedule, existing_user):
    request = RequestFactory().get(f"/basics/batches/{batch_with_section_and_batch_schedule.id}/edit/")
    request.user = existing_user

    response = EditView.as_view()(request, batch_with_section_and_batch_schedule.id)

    assert response.status_code == HttpResponse.status_code

def test_template_rendered_if_batch_exists(batch_with_section_and_batch_schedule, existing_user):
    client.post('/staff/login/', {'email': existing_user.email, 'password': 'password1234!'})

    response = client.get(reverse('batch_edit', kwargs={'batch_id': batch_with_section_and_batch_schedule.id}))

    assert response.status_code == HttpResponse.status_code
    assert 'basics/batch/edit.html' in (template.name for template in response.templates)

def test_template_rendered_again_if_sections_incorrectly_reduced(batch_with_section_and_batch_schedule, existing_user):
    section = batch_with_section_and_batch_schedule.section_set.first()
    incorrectly_reduced_number_of_sections = 0
    payload = {
        'start_date': '2022-01-01',
        'end_date': '2022-02-01',
        'sections': incorrectly_reduced_number_of_sections,
        'capacity': section.capacity,
        'batch-schedule-TOTAL_FORMS': ['1'],
        'batch-schedule-INITIAL_FORMS': ['1'],
        'batch-schedule-MIN_NUM_FORMS': ['0'],
        'batch-schedule-MAX_NUM_FORMS': ['7'],
        'batch-schedule-0-day': ['MON'],
        'batch-schedule-0-start_time': ['00:00:00'],
        'batch-schedule-0-end_time': ['02:00:00'],
    }
    client.post('/staff/login/', {
        'email': existing_user.email,
        'password': 'password1234!'}
    )

    freezer = freeze_time('2021-12-31')
    freezer.start()
    response = client.post(reverse('batch_edit', kwargs={'batch_id': batch_with_section_and_batch_schedule.id}), data=payload)
    freezer.stop()

    assert response.status_code == HttpResponse.status_code
    assert 'basics/batch/edit.html' in (template.name for template in response.templates)

def test_template_rendered_again_if_section_capacity_incorrectly_reduced(batch_with_section_and_batch_schedule, existing_user):
    section = batch_with_section_and_batch_schedule.section_set.first()
    incorrectly_reduced_section_capacity = section.capacity - 1
    payload = {
        'start_date': '2022-01-01',
        'end_date': '2022-02-01',
        'sections': Section.objects.all().count(),
        'capacity': incorrectly_reduced_section_capacity,
        'batch-schedule-TOTAL_FORMS': ['1'],
        'batch-schedule-INITIAL_FORMS': ['1'],
        'batch-schedule-MIN_NUM_FORMS': ['0'],
        'batch-schedule-MAX_NUM_FORMS': ['7'],
        'batch-schedule-0-day': ['MON'],
        'batch-schedule-0-start_time': ['00:00:00'],
        'batch-schedule-0-end_time': ['02:00:00'],
    }
    client.post('/staff/login/', {
        'email': existing_user.email,
        'password': 'password1234!'}
    )

    freezer = freeze_time('2021-12-31')
    freezer.start()
    response = client.post(reverse('batch_edit', kwargs={'batch_id': batch_with_section_and_batch_schedule.id}), data=payload)
    freezer.stop()

    assert response.status_code == HttpResponse.status_code
    assert 'basics/batch/edit.html' in (template.name for template in response.templates)

def test_valid_form_updates_and_creates_records(batch_with_section_and_batch_schedule, existing_user, mocker):
    new_start_date = batch_with_section_and_batch_schedule.start_date + timedelta(1)
    new_end_date = batch_with_section_and_batch_schedule.end_date + timedelta(1)

    new_sections_count = Section.objects.all().count() + 1
    section = batch_with_section_and_batch_schedule.section_set.first()
    section_capacity = section.capacity + 1

    new_batch_schedules_count = BatchSchedule.objects.all().count() + 1
    new_batch_schedule_day = 'TUE'
    new_batch_schedule_start_time = time(12, 0)
    new_batch_schedule_end_time = time(14, 0)

    payload = {
        'start_date': new_start_date,
        'end_date': new_end_date,
        'sections': new_sections_count,
        'capacity': section_capacity,
        'batch-schedule-TOTAL_FORMS': [f"{new_batch_schedules_count}"],
        'batch-schedule-INITIAL_FORMS': ['1'],
        'batch-schedule-MIN_NUM_FORMS': ['0'],
        'batch-schedule-MAX_NUM_FORMS': ['7'],
        'batch-schedule-0-day': ['MON'],
        'batch-schedule-0-start_time': ['00:00:00'],
        'batch-schedule-0-end_time': ['02:00:00'],
        'batch-schedule-1-day': [new_batch_schedule_day],
        'batch-schedule-1-start_time': [new_batch_schedule_start_time],
        'batch-schedule-1-end_time': [new_batch_schedule_end_time]
    }
    client.post('/staff/login/', {
        'email': existing_user.email,
        'password': 'password1234!'}
    )

    mocker.patch(
        'student.library.slack.Slack.create_channel',
        return_value='C1234567Q'
    )

    freezer = freeze_time('2022-1-2')
    freezer.start()
    response = client.post(reverse('batch_edit', kwargs={'batch_id': batch_with_section_and_batch_schedule.id}), data=payload)
    freezer.stop()

    assert response.status_code == HttpResponseRedirect.status_code
    assert response['Location'] == reverse('batch_detail', kwargs={'batch_id': batch_with_section_and_batch_schedule.id})

    batch = Batch.objects.first()
    assert batch.start_date == new_start_date
    assert batch.end_date == new_end_date
    assert batch.sections == new_sections_count
    assert batch.capacity == new_sections_count * section_capacity

    section_queryset = Section.objects.all()
    first_section = section_queryset.first()
    new_section = section_queryset.last()
    assert first_section.capacity == section_capacity
    assert section_queryset.count() == batch.sections
    Slack.create_channel.assert_called_once_with(f"{batch.number}-{new_section.number}")

    batchschedule_queryset = BatchSchedule.objects.all()
    new_batch_schedule = batchschedule_queryset.last()
    assert batchschedule_queryset.count() == new_batch_schedules_count
    assert new_batch_schedule.day == new_batch_schedule_day
    assert new_batch_schedule.start_time == new_batch_schedule_start_time
    assert new_batch_schedule.end_time == new_batch_schedule_end_time

def test_section_slack_channels_not_created_if_more_than_7_days_before_batch_starts(batch_with_section_and_batch_schedule, existing_user, mocker):
    batch_with_section_and_batch_schedule.start_date = date(2022, 1, 7)
    batch_with_section_and_batch_schedule.end_date = date(2022, 2, 1)
    new_sections_count = Section.objects.all().count() + 1
    section = batch_with_section_and_batch_schedule.section_set.first()

    payload = {
        'start_date': batch_with_section_and_batch_schedule.start_date,
        'end_date': batch_with_section_and_batch_schedule.end_date,
        'sections': new_sections_count,
        'capacity': section.capacity,
        'batch-schedule-TOTAL_FORMS': ['1'],
        'batch-schedule-INITIAL_FORMS': ['1'],
        'batch-schedule-MIN_NUM_FORMS': ['0'],
        'batch-schedule-MAX_NUM_FORMS': ['7'],
        'batch-schedule-0-day': ['MON'],
        'batch-schedule-0-start_time': ['00:00:00'],
        'batch-schedule-0-end_time': ['02:00:00'],
    }
    client.post('/staff/login/', {
        'email': existing_user.email,
        'password': 'password1234!'}
    )

    mocker.patch(
        'student.library.slack.Slack.create_channel',
        return_value='C1234567Q'
    )

    freezer = freeze_time('2021-12-31')
    freezer.start()
    client.post(reverse('batch_edit', kwargs={'batch_id': batch_with_section_and_batch_schedule.id}), data=payload)
    freezer.stop()

    Slack.create_channel.assert_not_called()
