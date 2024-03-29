from datetime import date, timedelta
from django.conf import settings
import factory

from staff.models import Batch
from staff.tests.factories.course_factory import CourseFactory

class BatchFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Batch

    course = factory.SubFactory(CourseFactory)
    number = 1
    start_date = date.today()
    end_date = date.today() + timedelta(days=settings.SWE_FUNDAMENTALS_COURSE_DURATION_IN_DAYS)
    capacity = 32
    sections = 2
    slack_channel_id = None
    price = settings.SWE_FUNDAMENTALS_REGISTRATION_FEE_SGD
    price_hk = settings.SWE_FUNDAMENTALS_REGISTRATION_FEE_HKD
    type = Batch.PART_TIME

    class Params:
        coding_basics = factory.Trait(
            course=factory.SubFactory(CourseFactory, coding_basics=True)
        )

        swe_fundamentals = factory.Trait(
            course=factory.SubFactory(CourseFactory, swe_fundamentals=True)
        )

        coding_bootcamp = factory.Trait(
            course=factory.SubFactory(CourseFactory, coding_bootcamp=True)
        )
