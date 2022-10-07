import datetime
from django.conf import settings
import pytest

from staff.models import Batch, BatchSchedule, Course

pytestmark = pytest.mark.django_db


class TestBatchScheduleCreation:
    def test_string_representation(self, batch_factory):
        batch = batch_factory()
        batch_schedule = BatchSchedule.objects.create(
            batch=batch,
            day='MON',
            iso_week_day='1',
            start_time=datetime.time(12, 00, 00),
            end_time=datetime.time(14, 00, 00),
        )

        string_representation = batch_schedule.__str__()

        assert string_representation == 'Mondays, 12:00PM to 2:00PM'
