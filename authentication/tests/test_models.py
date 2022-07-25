from datetime import date, timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
import pytest

from authentication.models import StudentUser
from staff.models import Batch, Course, Section
import student
from student.models.enrolment import Enrolment
from student.models.registration import Registration

User = get_user_model()
pytestmark = pytest.mark.django_db

email = 'someemail@domain.com'
first_name = 'FirstName'
last_name = 'LastName'
password = settings.PLACEHOLDER_PASSWORD

class TestUserManager:
    def test_empty_email_does_not_create_user(self):
        email = ''

        with pytest.raises(ValueError) as exception_info:
            User.objects.create_user(
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password
            )

        assert str(exception_info.value) == 'User must have an email address.'

class TestUser:
    def test_model_create(self):
        user = User.objects.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password
        )

        assert user.email == email
        assert user.first_name == first_name.upper()
        assert user.last_name == last_name.upper()
        assert user.password is not None

    def test_full_name(self):
        user = User.objects.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password
        )

        full_name = user.full_name()

        assert full_name == f'{first_name.upper()} {last_name.upper()}'

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
    current_enrolled_batches = student_user.current_enrolled_batches()

    assert list(current_enrolled_batches) == []
