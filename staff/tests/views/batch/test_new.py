from django.http import HttpResponse, HttpResponseRedirect
from django.test import Client, RequestFactory
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.urls import reverse
from freezegun import freeze_time
import pytest
from unittest.mock import patch, call

from staff.models import Batch, BatchSchedule, Course
from staff.views.batch import NewView

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
def course():
    yield Course.objects.create(name=settings.CODING_BASICS)


def test_anonymous_user_redirected_to_login():
    request = RequestFactory().get('/basics/batches/new/')
    request.user = AnonymousUser()

    response = NewView.as_view()(request)

    assert response.status_code == HttpResponseRedirect.status_code
    assert 'staff/login/?next=/basics/batches/' in response.url

def test_logged_in_user_can_access(course, existing_user):
    request = RequestFactory().get('/basics/batches/new/')
    request.user = existing_user

    response = NewView.as_view()(request)

    assert response.status_code == HttpResponse.status_code

@patch('staff.views.batch.set_up_section')
def test_valid_form_creates_records(mock_set_up_section, course, existing_user):
    number_of_sections = 6
    section_capacity = 18
    number_of_batch_schedules = 2

    payload = {
        'start_date': '2022-01-01',
        'end_date': '2022-02-01',
        'sections': number_of_sections,
        'capacity': section_capacity,
        'batch-schedule-TOTAL_FORMS': number_of_batch_schedules,
        'batch-schedule-INITIAL_FORMS': '0',
        'batch-schedule-MIN_NUM_FORMS': '0',
        'batch-schedule-MAX_NUM_FORMS': '7',
        'batch-schedule-0-day': 'MON',
        'batch-schedule-0-start_time': '00:00',
        'batch-schedule-0-end_time': '00:01',
        'batch-schedule-1-day': 'THU',
        'batch-schedule-1-start_time': '00:00',
        'batch-schedule-1-end_time': '00:01'
    }
    client.post('/staff/login/', {
        'email': existing_user.email,
        'password': 'password1234!'}
    )

    freezer = freeze_time('2021-12-31')
    freezer.start()
    response = client.post(reverse('batch_new'), data=payload)
    freezer.stop()

    assert response.status_code == HttpResponseRedirect.status_code

    assert Batch.objects.count() == 1
    batch = Batch.objects.first()
    assert batch.capacity == number_of_sections * section_capacity
    assert batch.course == Course.objects.get(name=settings.CODING_BASICS)

    calls = [call(batch, section_number, section_capacity) for section_number in range(1, batch.sections + 1)]
    mock_set_up_section.assert_has_calls(calls, any_order=True)
    assert BatchSchedule.objects.count() == number_of_batch_schedules
