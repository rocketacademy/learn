from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.test import Client, RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.urls import reverse
import pytest

from authentication.models import StudentUser
from staff.models import Section
from staff.views.enrolment import create_zoom_breakout_csv, ListView, prepare_zoom_breakout_csv_data
from student.models.enrolment import Enrolment
from student.models.registration import Registration

pytestmark = pytest.mark.django_db
client = Client()

@pytest.fixture()
def logged_in_existing_user():
    User = get_user_model()
    existing_user = User.objects.create_user(
        email='user@domain.com',
        first_name='FirstName',
        last_name='LastName',
        password='password1234!'
    )
    client.post('/staff/login/', {'email': existing_user.email, 'password': 'password1234!'})

    yield logged_in_existing_user

def test_enrolment_list_anonymous_user_redirected_to_login(batch_factory):
    batch = batch_factory()
    request = RequestFactory().get(f"/basics/batches/{batch.id}/enrolments/")
    request.user = AnonymousUser()

    response = ListView.as_view()(request)

    assert response.status_code == HttpResponseRedirect.status_code
    assert f"staff/login/?next=/basics/batches/{batch.id}/enrolments/" in response.url

def test_enrolment_list_logged_in_user_can_access(batch_factory, logged_in_existing_user):
    batch = batch_factory()
    response = client.get(reverse('enrolment_list', kwargs={'batch_id': batch.id}))

    assert response.status_code == HttpResponse.status_code
    assert 'basics/enrolment/list.html' in (template.name for template in response.templates)

def test_create_zoom_breakout_csv_outputs_csv_file(mocker, batch_factory):
    batch = batch_factory()
    student_email = 'bryan@test.com'
    room_name = 'room1'
    assert_value = [[room_name, student_email]]
    mocker.patch('staff.views.enrolment.prepare_zoom_breakout_csv_data', return_value=assert_value)
    request = RequestFactory().get(f"/basics/batches/{batch.id}/enrolments/")

    response = create_zoom_breakout_csv(request, batch.id)

    response_content = str(response.content)
    assert response.headers['Content-Type'] == 'text/csv'
    assert response.headers['Content-Disposition'] == f"attachment; filename=\"{batch.number}-zoom-breakout.csv\""
    assert student_email in response_content and room_name in response_content

def test_prepare_zoom_breakout_csv_data_returns_room_names_student_emails(batch_factory):
    batch = batch_factory()
    section = Section.objects.create(
        batch=batch,
        number=1,
        capacity=1
    )
    registration = Registration.objects.create(
        course=batch.course,
        batch=batch,
        first_name='FirstName',
        last_name='LastName',
        email='user@email.com',
        country_of_residence='SG',
        referral_channel='word_of_mouth'
    )
    student_user = StudentUser.objects.create(
        email='user@email.com',
        first_name='FirstName',
        last_name='LastName',
        password=settings.PLACEHOLDER_PASSWORD
    )
    first_enrolment = Enrolment.objects.create(
        registration=registration,
        batch=batch,
        section=section,
        student_user=student_user
    )
    second_registration = Registration.objects.create(
        course=batch.course,
        batch=batch,
        first_name='FirstName',
        last_name='LastName',
        email='user2@email.com',
        country_of_residence='SG',
        referral_channel='word_of_mouth'
    )
    second_student_user = StudentUser.objects.create(
        email='user2@email.com',
        first_name='FirstName',
        last_name='LastName',
        password=settings.PLACEHOLDER_PASSWORD
    )
    second_enrolment = Enrolment.objects.create(
        registration=second_registration,
        batch=batch,
        section=section,
        student_user=second_student_user
    )

    result = prepare_zoom_breakout_csv_data(batch.id)

    assert result == [
        ['Pre-assign Room Name', 'Email Address'],
        [f"room{first_enrolment.section.number}", first_enrolment.student_user.email],
        [f"room{second_enrolment.section.number}", second_enrolment.student_user.email]
    ]
