import factory

from staff.models import BatchSchedule
from staff.tests.factories.batch_factory import BatchFactory


class BatchScheduleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BatchSchedule

    batch = factory.SubFactory(BatchFactory)
    day = 'MON'
    iso_week_day = 1
    start_time = '10:00:00'
    end_time = '18:00:00'
