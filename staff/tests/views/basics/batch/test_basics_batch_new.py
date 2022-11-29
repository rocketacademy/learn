from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse, HttpResponseRedirect
from django.test import Client, RequestFactory
from django.urls import reverse
from freezegun import freeze_time
import pytest
from unittest.mock import patch

from staff.models import Batch, BatchSchedule, Course, Section
from staff.views.basics.basics_batch import NewView

pytestmark = pytest.mark.django_db
client = Client()


def test_anonymous_user_redirected_to_login():
    request = RequestFactory().get('/swe-fundamentals/batches/new/')
    request.user = AnonymousUser()

    response = NewView.as_view()(request)

    assert response.status_code == HttpResponseRedirect.status_code
    assert 'staff/login/?next=/swe-fundamentals/batches/new/' in response.url

def test_logged_in_user_can_access(course_factory, existing_user):
    course_factory(swe_fundamentals=True)
    request = RequestFactory().get(reverse('swe_fundamentals_batch_new'))
    request.user = existing_user

    response = NewView.as_view()(request)

    assert response.status_code == HttpResponse.status_code

@patch('staff.views.basics.basics_batch.create_batch_slack_channel')
def test_valid_form_creates_records(mock_create_batch_slack_channel, course_factory, existing_user):
    course_factory(swe_fundamentals=True)
    number_of_sections = 6
    section_capacity = 18
    number_of_batch_schedules = 2
    price = 199
    type = Batch.PART_TIME

    payload = {
        'start_date': '2022-01-01',
        'end_date': '2022-02-01',
        'sections': number_of_sections,
        'capacity': section_capacity,
        'price': price,
        'type': type,
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
        'password': settings.PLACEHOLDER_PASSWORD}
    )

    freezer = freeze_time('2021-12-31')
    freezer.start()
    response = client.post(reverse('swe_fundamentals_batch_new'), data=payload)
    freezer.stop()

    batch = Batch.swe_fundamentals_objects.first()
    assert response.status_code == HttpResponseRedirect.status_code
    assert response['location'] == reverse('swe_fundamentals_batch_detail', kwargs={'batch_id': batch.id})

    assert batch.capacity == number_of_sections * section_capacity
    assert batch.course == Course.objects.get(name=Course.SWE_FUNDAMENTALS)
    assert batch.price == price
    assert batch.type == type

    section_queryset = Section.objects.all()
    first_section = section_queryset.first()
    assert first_section.capacity == section_capacity
    assert section_queryset.count() == batch.sections

    mock_create_batch_slack_channel.assert_called_once()

    assert BatchSchedule.objects.count() == number_of_batch_schedules
