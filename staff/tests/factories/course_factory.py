import factory

from staff.models import Course

class CourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Course

    name = Course.CODING_BASICS
