from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.test import Client, RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
import pytest

from staff.views.course.swe_fundamentals.swe_fundamentals_enrolment import create_zoom_breakout_csv, ListView, prepare_zoom_breakout_csv_data

pytestmark = pytest.mark.django_db
client = Client()


def test_swe_fundamentals_batch_enrolment_list_anonymous_user_redirected_to_login(swe_fundamentals_batch):
    request = RequestFactory().get(f"/courses/swe-fundamentals/batches/{swe_fundamentals_batch.id}/enrolments/")
    request.user = AnonymousUser()

    response = ListView.as_view()(request)

    assert response.status_code == HttpResponseRedirect.status_code
    assert f"staff/login/?next=/courses/swe-fundamentals/batches/{swe_fundamentals_batch.id}/enrolments/" in response.url

def test_swe_fundamentals_batch_enrolment_list_contains_enrolments(enrolment_factory, existing_user):
    swe_fundamentals_enrolment = enrolment_factory(swe_fundamentals=True)
    client.post('/staff/login/', {'email': existing_user.email, 'password': settings.PLACEHOLDER_PASSWORD})

    response = client.get(reverse('swe_fundamentals_batch_enrolment_list', kwargs={'batch_id': swe_fundamentals_enrolment.batch.id}))

    assert response.status_code == HttpResponse.status_code
    assert list(response.context['enrolments']) == [swe_fundamentals_enrolment]
    assert 'course/swe_fundamentals/enrolment/list.html' in (template.name for template in response.templates)

def test_basics_batch_enrolment_list_contains_enrolments(enrolment_factory, existing_user):
    coding_basics_enrolment = enrolment_factory(coding_basics=True)
    client.post('/staff/login/', {'email': existing_user.email, 'password': settings.PLACEHOLDER_PASSWORD})

    response = client.get(reverse('swe_fundamentals_batch_enrolment_list', kwargs={'batch_id': coding_basics_enrolment.batch.id}))

    assert response.status_code == HttpResponse.status_code
    assert list(response.context['enrolments']) == [coding_basics_enrolment]
    assert 'course/swe_fundamentals/enrolment/list.html' in (template.name for template in response.templates)

def test_create_zoom_breakout_csv_outputs_csv_file_for_basics(mocker, coding_basics_batch):
    student_email = 'bryan@test.com'
    room_name = 'room1'
    assert_value = [[room_name, student_email]]
    mocker.patch('staff.views.course.swe_fundamentals.swe_fundamentals_enrolment.prepare_zoom_breakout_csv_data', return_value=assert_value)
    request = RequestFactory().get(f"/basics/batches/{coding_basics_batch.id}/enrolments/")

    response = create_zoom_breakout_csv(request, coding_basics_batch.id)

    response_content = str(response.content)
    assert response.headers['Content-Type'] == 'text/csv'
    assert response.headers['Content-Disposition'] == f"attachment; filename=\"{coding_basics_batch.number}-zoom-breakout.csv\""
    assert student_email in response_content and room_name in response_content

def test_create_zoom_breakout_csv_outputs_csv_file_for_swe_fundamentals(mocker, swe_fundamentals_batch):
    student_email = 'name@example.com'
    room_name = 'room1'
    mocker.patch(
        'staff.views.course.swe_fundamentals.swe_fundamentals_enrolment.prepare_zoom_breakout_csv_data',
        return_value=[
            [
                room_name,
                student_email
            ]
        ]
    )
    request = RequestFactory().get(f"/basics/batches/{swe_fundamentals_batch.id}/enrolments/")

    response = create_zoom_breakout_csv(request, swe_fundamentals_batch.id)

    response_content = str(response.content)
    assert response.headers['Content-Type'] == 'text/csv'
    assert response.headers['Content-Disposition'] == f"attachment; filename=\"{swe_fundamentals_batch.number}-zoom-breakout.csv\""
    assert student_email in response_content and room_name in response_content


def test_prepare_zoom_breakout_csv_data_returns_room_names_student_emails_for_basics(enrolment_factory):
    coding_basics_enrolment = enrolment_factory(coding_basics=True)

    result = prepare_zoom_breakout_csv_data(coding_basics_enrolment.batch.id)

    assert result == [
        ['Pre-assign Room Name', 'Email Address'],
        [f"room{coding_basics_enrolment.section.number}", coding_basics_enrolment.student_user.email],
    ]

def test_prepare_zoom_breakout_csv_data_returns_room_names_student_emails_for_swe_fundamentals(enrolment_factory):
    swe_fundamentals_enrolment = enrolment_factory(swe_fundamentals=True)

    result = prepare_zoom_breakout_csv_data(swe_fundamentals_enrolment.batch.id)

    assert result == [
        ['Pre-assign Room Name', 'Email Address'],
        [f"room{swe_fundamentals_enrolment.section.number}", swe_fundamentals_enrolment.student_user.email],
    ]
