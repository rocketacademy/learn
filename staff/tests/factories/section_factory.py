from django.utils.crypto import get_random_string
import factory

from staff.models import Section
from staff.tests.factories.batch_factory import BatchFactory


class SectionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Section

    batch = factory.SubFactory(BatchFactory)
    number = 1
    capacity = 12
    slack_channel_id = get_random_string(length=6)
