from datetime import date
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse, HttpResponseRedirect
from django.test import Client, RequestFactory
from django.urls import reverse
from freezegun import freeze_time
import pytest

from staff.models import Batch, BatchSchedule, Section
from staff.views.bootcamp.bootcamp_batch import NewView

pytestmark = pytest.mark.django_db
User = get_user_model()
client = Client()


def test_anonymous_user_redirected_to_login(course_factory):
    course_factory(coding_bootcamp=True)
    request = RequestFactory().get('/bootcamp/batches/new/')
    request.user = AnonymousUser()

    response = NewView.as_view()(request)

    assert response.status_code == HttpResponseRedirect.status_code
    assert 'staff/login/?next=/bootcamp/batches/' in response.url

def test_logged_in_user_can_access(course_factory, user_factory):
    course_factory(coding_bootcamp=True)
    existing_user = user_factory()
    request = RequestFactory().get('/bootcamp/batches/new/')
    request.user = existing_user
    form_id = 'create-batch-form'

    response = NewView.as_view()(request)

    assert response.status_code == HttpResponse.status_code
    assert form_id in str(response.content)

def test_valid_form_creates_records(course_factory):
    course_factory(coding_bootcamp=True)
    existing_user = User.objects.create_user(
        email='user@domain.com',
        first_name='FirstName',
        last_name='LastName',
        password=settings.PLACEHOLDER_PASSWORD
    )
    payload = {
        'start_date': '2022-10-14',
        'end_date': '2023-02-14',
        'sections': 2,
        'capacity': 6,
        'price': 7999,
        'type': Batch.FULL_TIME,
        'batch-schedule-TOTAL_FORMS': 2,
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
    client.post(
        '/staff/login/',
        {
            'email': existing_user.email,
            'password': settings.PLACEHOLDER_PASSWORD
        }
    )

    freezer = freeze_time('2021-10-01')
    freezer.start()
    response = client.post(reverse('bootcamp_batch_new'), data=payload)
    freezer.stop()

    batch = Batch.bootcamp_objects.first()
    assert response.status_code == HttpResponseRedirect.status_code
    assert response['location'] == reverse('bootcamp_batch_detail', kwargs={'batch_id': batch.id})

    assert str(batch.start_date) == payload['start_date']
    assert str(batch.end_date) == payload['end_date']
    assert batch.sections == payload['sections']
    assert batch.capacity == payload['sections'] * payload['capacity']
    assert batch.price == payload['price']
    assert str(batch.type) == payload['type']

    section_queryset = batch.section_set.all()
    assert section_queryset.first().capacity == payload['capacity']
    assert section_queryset.count() == payload['sections']

    batchschedule_queryset = batch.batchschedule_set.all()
    assert batchschedule_queryset.count() == payload['batch-schedule-TOTAL_FORMS']
    assert batchschedule_queryset.first().__str__() == 'Mondays, 12:00AM to 12:01AM'
    assert batchschedule_queryset.last().__str__() == 'Thursdays, 12:00AM to 12:01AM'
