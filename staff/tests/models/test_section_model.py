import datetime
from django.conf import settings
from django.contrib.auth import get_user_model
import pytest

from staff.models.batch import Batch
from staff.models.course import Course
from staff.models.section import Section
from student.models.enrolment import Enrolment

pytestmark = pytest.mark.django_db
User = get_user_model()


def test_fully_enrolled_returns_true():
    COURSE_DURATION_IN_DAYS = 35
    start_date = datetime.date.today()

    course = Course.objects.create(name=settings.CODING_BASICS)
    batch = Batch.objects.create(
        course=course,
        start_date=start_date,
        end_date=start_date + datetime.timedelta(COURSE_DURATION_IN_DAYS),
        capacity=18,
        sections=1
    )
    section = Section.objects.create(
        batch=batch,
        number=1,
        capacity=1
    )
    user = User.objects.create(
        email='user@email.com',
        first_name='FirstName',
        last_name='LastName',
        password=settings.PLACEHOLDER_PASSWORD
    )
    Enrolment.objects.create(
        batch=batch,
        section=section,
        user=user
    )

    result = section.fully_enrolled()

    assert result is True

def test_fully_enrolled_returns_false():
    COURSE_DURATION_IN_DAYS = 35
    start_date = datetime.date.today()

    course = Course.objects.create(name=settings.CODING_BASICS)
    batch = Batch.objects.create(
        course=course,
        start_date=start_date,
        end_date=start_date + datetime.timedelta(COURSE_DURATION_IN_DAYS),
        capacity=18,
        sections=1
    )
    section = Section.objects.create(
        batch=batch,
        number=1,
        capacity=1
    )

    result = section.fully_enrolled()

    assert result is False
