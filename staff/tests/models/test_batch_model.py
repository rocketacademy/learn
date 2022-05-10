import datetime
from django.conf import settings
import pytest

from staff.models import Batch, Course

pytestmark = pytest.mark.django_db

COURSE_NAME = settings.CODING_BASICS
COURSE_DURATION = 35

start_date = datetime.date.today()
end_date = start_date + datetime.timedelta(COURSE_DURATION)
capacity = 90
sections = 5

class TestBatchCreation:
    def test_batch_number_assigned_if_new_record(self):
        course = Course.objects.create(name=COURSE_NAME)
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

        assert first_batch.number == 1
        assert second_batch.number == 2

    def test_invalid_start_and_end_dates(self):
        course = Course.objects.create(name=COURSE_NAME)
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
