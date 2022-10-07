from datetime import date
from django.conf import settings
from django.http import HttpResponse
from django.test import Client
from django.urls import reverse
import pytest

from authentication.models import StudentUser
from staff.models import Section
from staff.models.certificate import Certificate
from student.models.enrolment import Enrolment
from student.models.registration import Registration

client = Client()
pytestmark = pytest.mark.django_db


@pytest.fixture()
def certificate(batch_factory):
    email = 'studentname@example.com'
    first_name = 'Student'
    last_name = 'Name'
    batch = batch_factory()
    section = Section.objects.create(
        batch=batch,
        number=1,
        capacity=1
    )
    registration = Registration.objects.create(
        course=batch.course,
        batch=batch,
        first_name=first_name,
        last_name=last_name,
        email=email,
        country_of_residence='SG',
        referral_channel='word_of_mouth'
    )
    student_user = StudentUser.objects.create_user(
        email=email,
        first_name=first_name,
        last_name=last_name,
        password=settings.PLACEHOLDER_PASSWORD
    )
    enrolment = Enrolment.objects.create(
        registration=registration,
        batch=batch,
        section=section,
        student_user=student_user
    )
    certificate = Certificate.objects.create(
        enrolment=enrolment,
        graduation_date=date.today()
    )

    yield certificate

def test_get_detail_renders_certificate_if_exists(certificate):
    response = client.get(
        reverse(
            'basics_certificate',
            kwargs={'certificate_credential': certificate.credential}
        )
    )

    assert response.status_code == HttpResponse.status_code
    assert response.context['certificate'] == certificate
    assert 'certificate/detail.html' in (template.name for template in response.templates)

def test_get_detail_renders_error_if_certificate_does_not_exist():
    incorrect_credential = 'ABCDEF'

    response = client.get(
        reverse(
            'basics_certificate',
            kwargs={'certificate_credential': incorrect_credential}
        )
    )

    assert response.status_code == HttpResponse.status_code
    assert response.context['certificate_credential'] == incorrect_credential
    assert 'certificate/error.html' in (template.name for template in response.templates)
