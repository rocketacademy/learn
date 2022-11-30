from datetime import date, timedelta
import pytest

pytestmark = pytest.mark.django_db


def test_current_enrolled_swe_fundamentals_batches_returns_batches_that_have_not_ended(enrolment_factory):
    swe_enrolment = enrolment_factory(swe_fundamentals=True)
    student_user = swe_enrolment.student_user

    current_enrolled_swe_fundamentals_batches = student_user.current_enrolled_swe_fundamentals_batches()

    assert list(current_enrolled_swe_fundamentals_batches) == [swe_enrolment.batch]

def test_current_enrolled_swe_fundamentals_batches_does_not_return_batches_that_have_ended(enrolment_factory):
    swe_enrolment = enrolment_factory(swe_fundamentals=True)
    swe_enrolment.batch.start_date = date.today() - timedelta(days=35)
    swe_enrolment.batch.end_date = date.today() - timedelta(days=1)
    swe_enrolment.batch.save()
    student_user = swe_enrolment.student_user

    current_enrolled_swe_fundamentals_batches = student_user.current_enrolled_swe_fundamentals_batches()

    assert list(current_enrolled_swe_fundamentals_batches) == []

def test_current_enrolled_swe_fundamentals_batches_returns_empty_if_no_enrolments(student_user, swe_fundamentals_batch):
    current_enrolled_swe_fundamentals_batches = student_user.current_enrolled_swe_fundamentals_batches()

    assert list(current_enrolled_swe_fundamentals_batches) == []

def test_current_enrolled_sections_returns_sections_in_batches_that_have_not_ended(enrolment_factory):
    swe_fundamentals_enrolment = enrolment_factory(swe_fundamentals=True)
    student_user = swe_fundamentals_enrolment.student_user

    current_enrolled_sections = student_user.current_enrolled_sections()

    assert list(current_enrolled_sections) == [swe_fundamentals_enrolment.section]

def test_current_enrolled_sections_returns_empty_if_batches_have_ended(enrolment_factory):
    swe_fundamentals_enrolment = enrolment_factory(swe_fundamentals=True)
    swe_fundamentals_enrolment.batch.start_date = date.today() - timedelta(days=35)
    swe_fundamentals_enrolment.batch.end_date = date.today() - timedelta(days=1)
    swe_fundamentals_enrolment.batch.save()
    student_user = swe_fundamentals_enrolment.student_user

    current_enrolled_sections = student_user.current_enrolled_sections()

    assert list(current_enrolled_sections) == []


def test_current_enrolled_sections_returns_empty_if_no_enrolments(student_user):
    current_enrolled_sections = student_user.current_enrolled_sections()

    assert list(current_enrolled_sections) == []
