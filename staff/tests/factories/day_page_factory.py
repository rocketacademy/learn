from factory import SubFactory, Trait
from factory.fuzzy import FuzzyText
from wagtail_factories import PageFactory

from staff.models import DayPage
from staff.tests.factories.batch_page_factory import BatchPageFactory

class DayPageFactory(PageFactory):
    class Meta:
        model = DayPage

    batch_page = SubFactory(BatchPageFactory, swe_fundamentals=True)
    body = FuzzyText(length=15)

    class Params:
        swe_fundamentals = Trait(
            batch_page=SubFactory(BatchPageFactory, swe_fundamentals=True)
        )

        coding_bootcamp = Trait(
            batch_page=SubFactory(BatchPageFactory, coding_bootcamp=True)
        )
