import datetime
from django.conf import settings
import pytest

from authentication.models import StudentUser
from staff.models import Course
from staff.models.certificate import Certificate

pytestmark = pytest.mark.django_db


@pytest.fixture()
def course():
    yield Course.objects.create(name=settings.CODING_BASICS)

@pytest.fixture()
def student_user():
    yield StudentUser.objects.create_user(
        first_name='Student',
        last_name='Name',
        email='studentname@example.com',
        password=settings.PLACEHOLDER_PASSWORD
    )

def test_credential_generated_if_new_object(course, student_user):
    certificate = Certificate(
        course=course,
        student_user=student_user,
        graduation_date=datetime.date.today()
    )

    certificate.save()

    assert len(certificate.credential) == 12
