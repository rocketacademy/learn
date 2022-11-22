import factory

from student.models.registration import Registration
from staff.tests.factories.batch_factory import BatchFactory
from staff.tests.factories.course_factory import CourseFactory


class RegistrationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Registration

    course = factory.SubFactory(CourseFactory)
    batch = factory.SubFactory(BatchFactory)
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    country_of_residence = 'SG'
    referral_channel = Registration.WORD_OF_MOUTH
    referral_code = None
