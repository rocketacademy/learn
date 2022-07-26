from datetime import date, timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
import pytest

from authentication.models import StudentUser
from staff.models import Batch, Course, Section
from student.models.enrolment import Enrolment
from student.models.registration import Registration

User = get_user_model()
pytestmark = pytest.mark.django_db

email = 'someemail@domain.com'
first_name = 'FirstName'
last_name = 'LastName'
password = settings.PLACEHOLDER_PASSWORD


@pytest.fixture()
def student_user():
    student_user = StudentUser.objects.create_user(
        email=email,
        first_name=first_name,
        last_name=last_name,
        password=settings.PLACEHOLDER_PASSWORD
    )

    yield student_user

@pytest.fixture()
def enrolment():
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
    student_user = StudentUser.objects.get(email=registration.email)
    enrolment = Enrolment.objects.create(
        registration=registration,
        batch=batch,
        section=section,
        student_user=student_user
    )

    yield enrolment

def test_current_enrolled_batches_returns_batches_that_have_not_ended(student_user, enrolment):
    current_enrolled_batches = student_user.current_enrolled_batches()

    assert list(current_enrolled_batches) == [enrolment.batch]

def test_current_enrolled_batches_does_not_return_batches_that_have_ended(student_user, enrolment):
    enrolment.batch.start_date = date.today() - timedelta(days=35)
    enrolment.batch.end_date = date.today() - timedelta(days=1)
    enrolment.batch.save()

    current_enrolled_batches = student_user.current_enrolled_batches()

    assert list(current_enrolled_batches) == []

def test_current_enrolled_batches_returns_empty_if_no_enrolments(student_user):
    course = Course.objects.create(name=settings.CODING_BASICS)
    batch = Batch.objects.create(
        course=course,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=1),
        capacity=1,
        sections=1,
    )

    current_enrolled_batches = student_user.current_enrolled_batches()

    assert list(current_enrolled_batches) == []
