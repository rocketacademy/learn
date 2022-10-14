import factory

from staff.models import Course

class CourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Course

    name = Course.CODING_BASICS

    class Params:
        coding_basics = factory.Trait(
            name=Course.CODING_BASICS
        )

        coding_bootcamp = factory.Trait(
            name=Course.CODING_BOOTCAMP
        )
