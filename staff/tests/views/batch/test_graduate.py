import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.test import Client, RequestFactory
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.urls import reverse
import pytest

from authentication.models import StudentUser
from staff.models import Batch, Course, Section
from staff.views.batch import GraduateView
from student.models.enrolment import Enrolment
from student.models.registration import Registration

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
    start_date = datetime.date.today() - datetime.timedelta(days=2)
    course = Course.objects.create(name=settings.CODING_BASICS)
    batch = Batch.objects.create(
        course=course,
        start_date=start_date,
        end_date=start_date + datetime.timedelta(days=1),
        capacity=90,
        sections=5
    )

    yield batch


def test_get_anonymous_user_redirected_to_login(batch):
    request = RequestFactory().get(f"/basics/batches/{batch.id}/graduate/")
    request.user = AnonymousUser()

    response = GraduateView.as_view()(request, batch.id)

    assert response.status_code == HttpResponseRedirect.status_code
    assert f"staff/login/?next=/basics/batches/{batch.id}/graduate/" in response.url

def test_get_logged_in_user_can_access(batch, existing_user):
    request = RequestFactory().get(f"/basics/batches/{batch.id}/graduate")
    request.user = existing_user

    response = GraduateView.as_view()(request, batch.id)

    assert response.status_code == HttpResponse.status_code

def test_get_template_rendered_if_batch_has_ended(batch, existing_user):
    client.post('/staff/login/', {'email': existing_user.email, 'password': 'password1234!'})

    response = client.get(reverse('batch_graduate', kwargs={'batch_id': batch.id}))

    assert response.status_code == HttpResponse.status_code
    assert 'basics/batch/graduate.html' in (template.name for template in response.templates)

def test_get_redirection_if_batch_has_not_ended(batch, existing_user):
    batch.end_date = datetime.date.today() + datetime.timedelta(days=1)
    batch.save()
    client.post('/staff/login/', {'email': existing_user.email, 'password': 'password1234!'})

    response = client.get(reverse('batch_graduate', kwargs={'batch_id': batch.id}))

    assert response.status_code == HttpResponseRedirect.status_code

def test_post_enrolment_statuses_updated(batch, existing_user):
    section = Section.objects.create(
        batch=batch,
        number=1,
        capacity=2
    )
    first_student_user = StudentUser.objects.create_user(
        first_name='First',
        last_name='Student',
        email='firststudent@example.com',
        password=settings.PLACEHOLDER_PASSWORD
    )
    first_registration = Registration.objects.create(
        course=batch.course,
        batch=batch,
        first_name=first_student_user.first_name,
        last_name=first_student_user.last_name,
        email=first_student_user.email,
        country_of_residence='SG',
        referral_channel='word_of_mouth'
    )
    first_enrolment = Enrolment.objects.create(
        registration=first_registration,
        batch=batch,
        section=section,
        student_user=first_student_user,
        status=Enrolment.ENROLLED
    )
    second_student_user = StudentUser.objects.create_user(
        first_name='Second',
        last_name='Student',
        email='secondstudent@example.com',
        password=settings.PLACEHOLDER_PASSWORD
    )
    second_registration = Registration.objects.create(
        course=batch.course,
        batch=batch,
        first_name=second_student_user.first_name,
        last_name=second_student_user.last_name,
        email=second_student_user.email,
        country_of_residence='SG',
        referral_channel='word_of_mouth'
    )
    second_enrolment = Enrolment.objects.create(
        registration=second_registration,
        batch=batch,
        section=section,
        student_user=second_student_user,
        status=Enrolment.ENROLLED
    )
    client.post('/staff/login/', {'email': existing_user.email, 'password': 'password1234!'})

    client.post(
        reverse(
            'batch_graduate',
            kwargs={'batch_id': batch.id}
        ),
        data={
            'enrolment': [
                first_enrolment.id,
                second_enrolment.id
            ]
        }
    )

    first_enrolment.refresh_from_db()
    second_enrolment.refresh_from_db()
    assert first_enrolment.status == Enrolment.PASSED
    assert second_enrolment.status == Enrolment.PASSED
