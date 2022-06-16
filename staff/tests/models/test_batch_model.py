import datetime
from django.conf import settings
import pytest

from authentication.models import StudentUser
from staff.models import Batch, BatchSchedule, Course, Section
from student.models.enrolment import Enrolment

pytestmark = pytest.mark.django_db

COURSE_DURATION_IN_DAYS = 35

start_date = datetime.date.today()
end_date = start_date + datetime.timedelta(COURSE_DURATION_IN_DAYS)
capacity = 90
sections = 5

@pytest.fixture()
def course():
    course = Course.objects.create(name=settings.CODING_BASICS)

    yield course

@pytest.fixture()
def batch():
    course = Course.objects.create(name=settings.CODING_BASICS)
    batch = Batch.objects.create(
        course=course,
        start_date=start_date,
        end_date=end_date,
        capacity=capacity,
        sections=sections
    )

    yield batch

def test_string_representation(batch):
    string_representation = batch.__str__()

    assert string_representation == 'Batch 17'

def test_batch_number_assigned_if_new_record(course):
    first_batch = Batch.objects.create(
        course=course,
        start_date=start_date,
        end_date=end_date,
        capacity=capacity,
        sections=sections
    )
    second_batch = Batch.objects.create(
        course=course,
        start_date=start_date,
        end_date=end_date,
        capacity=capacity,
        sections=sections
    )

    assert first_batch.number == 17
    assert second_batch.number == 18

def test_invalid_start_and_end_dates(course):
    end_date = start_date - datetime.timedelta(1)

    with pytest.raises(ValueError) as exception_info:
        Batch.objects.create(
            course=course,
            start_date=start_date,
            end_date=end_date,
            capacity=capacity,
            sections=sections
        )

    assert str(exception_info.value) == 'Batch end date should be after start date', 'Should raise ValueError with message if end date not after start date'

def test_html_formatted_batch_schedules(batch):
    BatchSchedule.objects.create(
        batch=batch,
        day='MON',
        iso_week_day='1',
        start_time=datetime.time(12, 00, 00),
        end_time=datetime.time(14, 00, 00),
    )
    BatchSchedule.objects.create(
        batch=batch,
        day='FRI',
        iso_week_day='5',
        start_time=datetime.time(12, 00, 00),
        end_time=datetime.time(14, 00, 00),
    )

    html_formatted_batch_schedules = Batch.html_formatted_batch_schedules(batch)

    assert html_formatted_batch_schedules == '<small>Mondays, 12:00PM to 2:00PM</small><br><small>Fridays, 12:00PM to 2:00PM</small><br>'

def test_next_enrollable_section(batch):
    first_student_user = StudentUser.objects.create(
        email='user@email.com',
        first_name='FirstName',
        last_name='LastName',
        password=settings.PLACEHOLDER_PASSWORD
    )
    fully_enrolled_section = Section.objects.create(
        batch=batch,
        number=1,
        capacity=1
    )
    enrollable_section = Section.objects.create(
        batch=batch,
        number=1,
        capacity=1
    )
    Enrolment.objects.create(
        batch=batch,
        section=fully_enrolled_section,
        student_user=first_student_user
    )

    result = batch.next_enrollable_section()

    assert result == enrollable_section

def test_fully_enrolled_returns_true(course):
    student_user = StudentUser.objects.create(
        email='user@email.com',
        first_name='FirstName',
        last_name='LastName',
        password=settings.PLACEHOLDER_PASSWORD
    )
    batch = Batch.objects.create(
        course=course,
        start_date=start_date,
        end_date=end_date,
        capacity=1,
        sections=1
    )
    section = Section.objects.create(
        batch=batch,
        number=1,
        capacity=1
    )
    Enrolment.objects.create(
        batch=batch,
        section=section,
        student_user=student_user
    )

    result = batch.fully_enrolled()

    assert result is True

def test_fully_enrolled_returns_false_when_there_is_still_space(course):
    student_user = StudentUser.objects.create(
        email='user@email.com',
        first_name='FirstName',
        last_name='LastName',
        password=settings.PLACEHOLDER_PASSWORD
    )
    batch = Batch.objects.create(
        course=course,
        start_date=start_date,
        end_date=end_date,
        capacity=2,
        sections=1
    )
    section = Section.objects.create(
        batch=batch,
        number=1,
        capacity=2
    )
    Enrolment.objects.create(
        batch=batch,
        section=section,
        student_user=student_user
    )

    result = batch.fully_enrolled()

    assert result is False
