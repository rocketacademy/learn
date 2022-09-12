import datetime
from django.conf import settings
from django.http import HttpResponse
from django.test import Client
from django.urls import reverse
import pytest

from authentication.models import StudentUser
from staff.models import Course
from staff.models.certificate import Certificate

client = Client()
pytestmark = pytest.mark.django_db


@pytest.fixture()
def certificate():
    course = Course.objects.create(name=settings.CODING_BASICS)
    student_user = StudentUser.objects.create_user(
        first_name='Student',
        last_name='Name',
        email='studentname@example.com',
        password=settings.PLACEHOLDER_PASSWORD
    )
    certificate = Certificate.objects.create(
        course=course,
        student_user=student_user,
        graduation_date=datetime.date.today()
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
