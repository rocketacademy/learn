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

def test_weeks_to_start_method_returns_calculated_weeks():
    start_date = datetime.date.today() + datetime.timedelta(weeks=7)
    end_date = start_date + datetime.timedelta(weeks=6)
    course = Course.objects.create(name=settings.CODING_BASICS)
    batch = Batch.objects.create(
        course=course,
        start_date=start_date,
        end_date=end_date,
        capacity=34,
        sections=2
    )

    result = batch.weeks_to_start()

    assert result == 7

def test_weeks_to_start_method_returns_zero_weeks_if_days_under_7():
    start_date = datetime.date.today() + datetime.timedelta(days=6)
    end_date = start_date + datetime.timedelta(weeks=6)
    course = Course.objects.create(name=settings.CODING_BASICS)
    batch = Batch.objects.create(
        course=course,
        start_date=start_date,
        end_date=end_date,
        capacity=34,
        sections=2
    )

    result = batch.weeks_to_start()

    assert result == 0

def test_current_price_method_returns_original_price_under_two_weeks():
    start_date = datetime.date.today() + datetime.timedelta(days=13)
    end_date = start_date + datetime.timedelta(weeks=6)
    course = Course.objects.create(name=settings.CODING_BASICS)
    batch = Batch.objects.create(
        course=course,
        start_date=start_date,
        end_date=end_date,
        capacity=34,
        sections=2
    )

    current_price = batch.current_price()

    assert current_price == 199

def test_current_price_method_returns_discounted_price_at_two_weeks():
    start_date = datetime.date.today() + datetime.timedelta(days=14)
    end_date = start_date + datetime.timedelta(weeks=6)
    course = Course.objects.create(name=settings.CODING_BASICS)
    batch = Batch.objects.create(
        course=course,
        start_date=start_date,
        end_date=end_date,
        capacity=34,
        sections=2
    )

    current_price = batch.current_price()

    assert current_price == 189

def test_current_price_method_returns_capped_discounted_price_at_40_dollars():
    start_date = datetime.date.today() + datetime.timedelta(weeks=8)
    end_date = start_date + datetime.timedelta(weeks=6)
    course = Course.objects.create(name=settings.CODING_BASICS)
    batch = Batch.objects.create(
        course=course,
        start_date=start_date,
        end_date=end_date,
        capacity=34,
        sections=2
    )

    current_price = batch.current_price()

    assert current_price == 159


def test_html_formatted_batch_price_returns_base_price_formatting_under_two_weeks(course):
    start_date = datetime.date.today() + datetime.timedelta(days=13)
    end_date = start_date + datetime.timedelta(weeks=6)
    course = Course.objects.create(name=settings.CODING_BASICS)
    batch = Batch.objects.create(
        course=course,
        start_date=start_date,
        end_date=end_date,
        capacity=34,
        sections=2
    )

    html_formatted_batch_price = batch.html_formatted_batch_price()

    assert html_formatted_batch_price == "<span class='float-end d-none d-xl-block'>$199</span><div class='lh-lg d-xl-none my-10'>$199<div>"

def test_html_formatted_batch_price_returns_discounted_price_formatting_after_13_days(course):
    start_date = datetime.date.today() + datetime.timedelta(days=14)
    end_date = start_date + datetime.timedelta(weeks=6)
    course = Course.objects.create(name=settings.CODING_BASICS)
    batch = Batch.objects.create(
        course=course,
        start_date=start_date,
        end_date=end_date,
        capacity=34,
        sections=2
    )

    html_formatted_batch_price = batch.html_formatted_batch_price()

    required_string = "<span class='float-end d-none d-xl-block'>$189  <span class='text-secondary'><s>$199</s></span></span>"
    required_string += "<div class='lh-lg d-xl-none'>$189  <span class='text-secondary'><s>$199</s></span></div>"
    assert html_formatted_batch_price == required_string
