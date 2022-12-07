from django.utils.text import slugify
from factory import LazyAttribute, SubFactory, Trait
from factory.fuzzy import FuzzyText
from wagtail_factories import PageFactory

from staff.models import CoursePage
from staff.tests.factories.course_factory import CourseFactory

class CoursePageFactory(PageFactory):
    class Meta:
        model = CoursePage

    title = FuzzyText(length=15)
    slug = LazyAttribute(lambda object: slugify(object.course.name.replace('_', '-')))
    intro = FuzzyText(length=20)
    course = SubFactory(CourseFactory, swe_fundamentals=True)

    class Params:
        swe_fundamentals = Trait(
            course=SubFactory(CourseFactory, swe_fundamentals=True)
        )

        coding_bootcamp = Trait(
            course=SubFactory(CourseFactory, coding_bootcamp=True)
        )
