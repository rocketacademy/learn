from django.conf import settings
import pytest

from authentication.models import StudentUser
from staff.models.section import Section
from student.models.enrolment import Enrolment

pytestmark = pytest.mark.django_db


def test_fully_enrolled_returns_true(batch_factory):
    batch = batch_factory()
    section = Section.objects.create(
        batch=batch,
        number=1,
        capacity=1
    )
    student_user = StudentUser.objects.create(
        email='user@email.com',
        first_name='FirstName',
        last_name='LastName',
        password=settings.PLACEHOLDER_PASSWORD
    )
    Enrolment.objects.create(
        batch=batch,
        section=section,
        student_user=student_user
    )

    result = section.fully_enrolled()

    assert result is True

def test_fully_enrolled_returns_false(batch_factory):
    batch = batch_factory()
    section = Section.objects.create(
        batch=batch,
        number=1,
        capacity=1
    )

    result = section.fully_enrolled()

    assert result is False
