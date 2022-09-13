from datetime import date, timedelta
from django.conf import settings
from django.http import HttpResponse
from django.test import Client
from django.urls import reverse
import pytest

from authentication.models import StudentUser
from staff.models import Batch, Course, Section
from staff.models.certificate import Certificate
from student.models.enrolment import Enrolment
from student.models.registration import Registration

client = Client()
pytestmark = pytest.mark.django_db


@pytest.fixture()
def certificate():
    email = 'studentname@example.com'
    first_name = 'Student'
    last_name = 'Name'
    course = Course.objects.create(name=settings.CODING_BASICS)
    batch = Batch.objects.create(
        course=course,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=1),
        capacity=1,
        sections=1,
    )
    section = Section.objects.create(
        batch=batch,
        number=1,
        capacity=1
    )
    registration = Registration.objects.create(
        course=course,
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
        student_user=student_user,
        graduation_date=date.today()
    )

    yield certificate

def test_get_detail_renders_template(certificate):
    response = client.get(
        reverse(
            'basics_certificate',
            kwargs={'certificate_credential': certificate.credential}
        )
    )

    assert response.status_code == HttpResponse.status_code
    assert response.context['certificate'] == certificate
    assert 'certificate/detail.html' in (template.name for template in response.templates)
