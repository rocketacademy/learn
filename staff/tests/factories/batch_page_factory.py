from django.utils.text import slugify
from factory import LazyAttribute, SubFactory, Trait
from factory.fuzzy import FuzzyText
from wagtail_factories import PageFactory

from staff.models import BatchPage
from staff.tests.factories.batch_factory import BatchFactory

class BatchPageFactory(PageFactory):
    class Meta:
        model = BatchPage

    title = FuzzyText(length=15)
    slug = LazyAttribute(lambda object: slugify(object.batch.number))
    intro = FuzzyText(length=20)
    batch = SubFactory(BatchFactory, swe_fundamentals=True)

    class Params:
        swe_fundamentals = Trait(
            batch=SubFactory(BatchFactory, swe_fundamentals=True)
        )

        coding_bootcamp = Trait(
            batch=SubFactory(BatchFactory, coding_bootcamp=True)
        )
