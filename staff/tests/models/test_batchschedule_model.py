import datetime
from django.conf import settings
import pytest

from staff.models import Batch, BatchSchedule, Course

pytestmark = pytest.mark.django_db


@pytest.fixture()
def batch():
    COURSE_DURATION = 35
    start_date = datetime.date.today()
    end_date = start_date + datetime.timedelta(COURSE_DURATION)
    capacity = 90
    sections = 5

    course = Course.objects.create(name=settings.CODING_BASICS)
    batch = Batch.objects.create(
        course=course,
        start_date=start_date,
        end_date=end_date,
        capacity=capacity,
        sections=sections
    )

    yield batch

class TestBatchScheduleCreation:
    def test_string_representation(self, batch):
        batch_schedule = BatchSchedule.objects.create(
            batch=batch,
            day='MON',
            start_time=datetime.time(12, 00, 00),
            end_time=datetime.time(14, 00, 00),
        )

        string_representation = batch_schedule.__str__()

        assert string_representation == 'Mondays, 12:00PM to 2:00PM'
