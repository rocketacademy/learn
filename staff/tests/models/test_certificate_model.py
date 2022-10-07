from datetime import date
from django.conf import settings
import pytest

from authentication.models import StudentUser
from staff.models import Section
from staff.models.certificate import Certificate
from student.models.enrolment import Enrolment
from student.models.registration import Registration

pytestmark = pytest.mark.django_db


@pytest.fixture()
def enrolment(batch_factory):
    email = 'studentname@example.com'
    first_name = 'Student'
    last_name = 'Name'
    batch = batch_factory.create()
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

    yield enrolment

def test_credential_generated_if_new_object(enrolment):
    certificate = Certificate(
        enrolment=enrolment,
        graduation_date=date.today()
    )

    certificate.save()

    assert len(certificate.credential) == 12
