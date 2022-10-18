from datetime import date, timedelta
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse, HttpResponseRedirect
from django.test import Client, RequestFactory
from django.urls import reverse
from freezegun import freeze_time
import pytest

from staff.views.bootcamp.bootcamp_batch import EditView

pytestmark = pytest.mark.django_db
client = Client()


def test_bootcamp_batch_edit_anonymous_user_redirected_to_login(coding_bootcamp_batch):
    request = RequestFactory().get(f"/bootcamp/{coding_bootcamp_batch.id}/edit/")
    request.user = AnonymousUser()

    response = EditView.as_view()(request, coding_bootcamp_batch.id)

    assert response.status_code == HttpResponseRedirect.status_code
    assert f"staff/login/?next=/bootcamp/{coding_bootcamp_batch.id}/edit/" in response.url

def test_bootcamp_batch_edit_template_rendered_for_logged_in_user(coding_bootcamp_batch, existing_user):
    client.post('/staff/login/', {'email': existing_user.email, 'password': settings.PLACEHOLDER_PASSWORD})

    response = client.get(reverse('bootcamp_batch_edit', kwargs={'batch_id': coding_bootcamp_batch.id}))

    assert response.status_code == HttpResponse.status_code
    assert 'bootcamp/batch/edit.html' in (template.name for template in response.templates)

def test_template_rendered_again_if_payload_invalid(coding_bootcamp_batch, existing_user):
    invalid_price = 0
    payload = {
        'start_date': str(coding_bootcamp_batch.start_date),
        'end_date': str(coding_bootcamp_batch.end_date),
        'sections': coding_bootcamp_batch.sections,
        'capacity': coding_bootcamp_batch.capacity,
        'price': invalid_price,
        'type': coding_bootcamp_batch.type,
        'batch-schedule-TOTAL_FORMS': ['1'],
        'batch-schedule-INITIAL_FORMS': ['1'],
        'batch-schedule-MIN_NUM_FORMS': ['0'],
        'batch-schedule-MAX_NUM_FORMS': ['7'],
        'batch-schedule-0-day': [coding_bootcamp_batch.batchschedule_set.first().day],
        'batch-schedule-0-start_time': [coding_bootcamp_batch.batchschedule_set.first().start_time],
        'batch-schedule-0-end_time': [coding_bootcamp_batch.batchschedule_set.first().end_time],
    }
    client.post('/staff/login/', {'email': existing_user.email, 'password': settings.PLACEHOLDER_PASSWORD})

    freezer = freeze_time(date.today() - timedelta(days=1))
    freezer.start()
    response = client.post(reverse('bootcamp_batch_edit', kwargs={'batch_id': coding_bootcamp_batch.id}), data=payload)
    freezer.stop()

    assert response.status_code == HttpResponse.status_code
    assert 'bootcamp/batch/edit.html' in (template.name for template in response.templates)

def test_records_updated_if_payload_valid(coding_bootcamp_batch, existing_user):
    valid_price = coding_bootcamp_batch.price + 1
    payload = {
        'start_date': str(coding_bootcamp_batch.start_date),
        'end_date': str(coding_bootcamp_batch.end_date),
        'sections': coding_bootcamp_batch.sections,
        'capacity': coding_bootcamp_batch.capacity,
        'price': valid_price,
        'type': coding_bootcamp_batch.type,
        'batch-schedule-TOTAL_FORMS': ['1'],
        'batch-schedule-INITIAL_FORMS': ['1'],
        'batch-schedule-MIN_NUM_FORMS': ['0'],
        'batch-schedule-MAX_NUM_FORMS': ['7'],
        'batch-schedule-0-day': [coding_bootcamp_batch.batchschedule_set.first().day],
        'batch-schedule-0-start_time': [coding_bootcamp_batch.batchschedule_set.first().start_time],
        'batch-schedule-0-end_time': [coding_bootcamp_batch.batchschedule_set.first().end_time],
    }

    client.post('/staff/login/', {'email': existing_user.email, 'password': settings.PLACEHOLDER_PASSWORD})

    freezer = freeze_time(date.today() - timedelta(days=1))
    freezer.start()
    response = client.post(reverse('bootcamp_batch_edit', kwargs={'batch_id': coding_bootcamp_batch.id}), data=payload)
    freezer.stop()

    assert response.status_code == HttpResponseRedirect.status_code
    assert response['location'] == reverse('bootcamp_batch_detail', kwargs={'batch_id': coding_bootcamp_batch.id})
    coding_bootcamp_batch.refresh_from_db()
    assert coding_bootcamp_batch.price == valid_price
