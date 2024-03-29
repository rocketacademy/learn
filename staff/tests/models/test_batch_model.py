from datetime import date, time, timedelta
from django.conf import settings
import pytest

from authentication.models import StudentUser
from staff.models import Batch, BatchSchedule, Section
from student.models.enrolment import Enrolment

pytestmark = pytest.mark.django_db


def test_string_representation(batch_factory):
    batch = batch_factory()

    string_representation = batch.__str__()

    assert string_representation == 'Batch 17'

def test_number_assigned_if_new_basics_batch_record(batch_factory, course_factory):
    coding_basics_course = course_factory(coding_basics=True)

    first_batch = batch_factory.create(course=coding_basics_course)
    second_batch = batch_factory.create(course=coding_basics_course)

    assert first_batch.number == 17
    assert second_batch.number == 18

def test_number_not_reassigned_if_existing_basics_batch_record_saved(batch_factory, course_factory):
    coding_basics_course = course_factory(coding_basics=True)
    first_batch = batch_factory(course=coding_basics_course)
    second_batch = batch_factory(course=coding_basics_course)
    new_capacity = 100

    first_batch.capacity = new_capacity
    first_batch.save()

    assert first_batch.number == 17

def test_number_assigned_if_new_swe_fundamentals_batch_record(batch_factory, course_factory):
    swe_fundamentals_course = course_factory(swe_fundamentals=True)

    first_batch = batch_factory(course=swe_fundamentals_course)
    second_batch = batch_factory(course=swe_fundamentals_course)

    assert first_batch.number == 21
    assert second_batch.number == 22

def test_number_not_reassigned_if_existing_swe_fundamentals_batch_record_saved(batch_factory, course_factory):
    swe_fundamentals_course = course_factory(swe_fundamentals=True)
    first_batch = batch_factory(course=swe_fundamentals_course)
    second_batch = batch_factory(course=swe_fundamentals_course)
    new_capacity = 100

    first_batch.capacity = new_capacity
    first_batch.save()

    assert first_batch.number == 21

def test_number_assigned_if_new_fulltime_bootcamp_batch_record(batch_factory, course_factory):
    coding_bootcamp_course = course_factory(coding_bootcamp=True)

    first_batch = batch_factory.create(course=coding_bootcamp_course, type=Batch.FULL_TIME)
    second_batch = batch_factory.create(course=coding_bootcamp_course, type=Batch.FULL_TIME)

    assert first_batch.number == 10
    assert second_batch.number == 11

def test_number_not_reassigned_if_existing_fulltime_bootcamp_batch_record_saved(batch_factory, course_factory):
    coding_bootcamp_course = course_factory(coding_bootcamp=True)
    first_batch = batch_factory(course=coding_bootcamp_course, type=Batch.FULL_TIME)
    second_batch = batch_factory(course=coding_bootcamp_course, type=Batch.FULL_TIME)
    new_capacity = 100

    first_batch.capacity = new_capacity
    first_batch.save()

    assert first_batch.number == 10

def test_number_assigned_if_new_parttime_bootcamp_batch_record(batch_factory, course_factory):
    coding_bootcamp_course = course_factory(coding_bootcamp=True)

    first_batch = batch_factory.create(course=coding_bootcamp_course, type=Batch.PART_TIME)
    second_batch = batch_factory.create(course=coding_bootcamp_course, type=Batch.PART_TIME)

    assert first_batch.number == 6
    assert second_batch.number == 7

def test_number_not_reassigned_if_existing_parttime_bootcamp_batch_record_saved(batch_factory, course_factory):
    coding_bootcamp_course = course_factory(coding_bootcamp=True)
    first_batch = batch_factory(course=coding_bootcamp_course, type=Batch.PART_TIME)
    second_batch = batch_factory(course=coding_bootcamp_course, type=Batch.PART_TIME)
    new_capacity = 100

    first_batch.capacity = new_capacity
    first_batch.save()

    assert first_batch.number == 6

def test_invalid_start_and_end_dates(batch_factory):
    start_date = date.today()
    end_date = start_date - timedelta(days=1)

    with pytest.raises(ValueError) as exception_info:
        batch_factory(start_date=start_date, end_date=end_date)

    assert str(exception_info.value) == 'Batch end date should be after start date', 'Should raise ValueError with message if end date not after start date'

def test_html_formatted_batch_schedules(batch_factory):
    coding_basics_batch = batch_factory()
    BatchSchedule.objects.create(
        batch=coding_basics_batch,
        day='MON',
        iso_week_day='1',
        start_time=time(12, 00, 00),
        end_time=time(14, 00, 00),
    )
    BatchSchedule.objects.create(
        batch=coding_basics_batch,
        day='FRI',
        iso_week_day='5',
        start_time=time(12, 00, 00),
        end_time=time(14, 00, 00),
    )

    html_formatted_batch_schedules = Batch.html_formatted_batch_schedules(coding_basics_batch)

    assert html_formatted_batch_schedules == 'Mondays, 12:00PM to 2:00PM<br>Fridays, 12:00PM to 2:00PM<br>'

def test_next_enrollable_section(batch_factory):
    batch = batch_factory()
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

def test_fully_enrolled_returns_true(batch_factory):
    batch = batch_factory(capacity=1, sections=1)
    student_user = StudentUser.objects.create(
        email='user@email.com',
        first_name='FirstName',
        last_name='LastName',
        password=settings.PLACEHOLDER_PASSWORD
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

def test_fully_enrolled_returns_false_when_there_is_still_space(batch_factory):
    batch = batch_factory(capacity=2, sections=1)
    student_user = StudentUser.objects.create(
        email='user@email.com',
        first_name='FirstName',
        last_name='LastName',
        password=settings.PLACEHOLDER_PASSWORD
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

def test_weeks_to_start_method_returns_calculated_weeks(batch_factory):
    start_date = date.today() + timedelta(weeks=7)
    end_date = start_date + timedelta(weeks=6)
    batch = batch_factory(start_date=start_date, end_date=end_date)

    result = batch.weeks_to_start()

    assert result == 7

def test_weeks_to_start_method_returns_zero_weeks_if_days_under_7(batch_factory):
    start_date = date.today() + timedelta(days=6)
    end_date = start_date + timedelta(weeks=6)
    batch = batch_factory(start_date=start_date, end_date=end_date)

    result = batch.weeks_to_start()

    assert result == 0

def test_early_bird_method_returns_0_under_two_weeks(batch_factory):
    start_date = date.today() + timedelta(days=13)
    end_date = start_date + timedelta(weeks=6)
    batch = batch_factory(start_date=start_date, end_date=end_date)

    early_bird_discount = batch.early_bird_discount()

    assert early_bird_discount == 0

def test_early_bird_method_returns_first_tier_discounted_price_at_three_weeks(batch_factory):
    start_date = date.today() + timedelta(days=21)
    end_date = start_date + timedelta(weeks=6)
    batch = batch_factory(start_date=start_date, end_date=end_date)

    early_bird_discount = batch.early_bird_discount()

    assert early_bird_discount == settings.SWE_FUNDAMENTALS_TIERED_DISCOUNT_PER_WEEK

def test_early_bird_method_returns_capped_discounted_price(batch_factory):
    start_date = date.today() + timedelta(weeks=8)
    end_date = start_date + timedelta(weeks=6)
    batch = batch_factory(start_date=start_date, end_date=end_date)

    early_bird_discount = batch.early_bird_discount()

    assert early_bird_discount == settings.SWE_FUNDAMENTALS_TIERED_DISCOUNT_CAP

def test_html_formatted_batch_price_returns_base_price_formatting_under_three_weeks(batch_factory):
    start_date = date.today() + timedelta(days=20)
    end_date = start_date + timedelta(weeks=6)
    batch = batch_factory(start_date=start_date, end_date=end_date)

    html_formatted_batch_price = batch.html_formatted_batch_price()

    assert "S$199" in html_formatted_batch_price

def test_html_formatted_batch_price_returns_discounted_price_formatting_after_20_days(batch_factory):
    start_date = date.today() + timedelta(days=21)
    end_date = start_date + timedelta(weeks=6)
    batch = batch_factory(start_date=start_date, end_date=end_date)

    html_formatted_batch_price = batch.html_formatted_batch_price()

    assert "S$189" in html_formatted_batch_price
    assert "S$199" in html_formatted_batch_price
