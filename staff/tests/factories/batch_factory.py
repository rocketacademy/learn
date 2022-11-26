from datetime import date, timedelta
from django.conf import settings
import factory

from staff.models import Batch
from staff.tests.factories.course_factory import CourseFactory

COURSE_DURATION_IN_DAYS = 35

class BatchFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Batch

    course = factory.SubFactory(CourseFactory)
    number = 1
    start_date = date.today()
    end_date = date.today() + timedelta(days=COURSE_DURATION_IN_DAYS)
    capacity = 32
    sections = 2
    slack_channel_id = None
    price = settings.SWE_FUNDAMENTALS_REGISTRATION_FEE_SGD
    type = Batch.PART_TIME

    class Params:
        swe_fundamentals = factory.Trait(
            course=factory.SubFactory(CourseFactory, swe_fundamentals=True)
        )

        coding_bootcamp = factory.Trait(
            course=factory.SubFactory(CourseFactory, coding_bootcamp=True)
        )
