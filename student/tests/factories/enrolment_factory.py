import factory

from authentication.tests.factories.student_user_factory import StudentUserFactory
from student.models.enrolment import Enrolment
from student.tests.factories.registration_factory import RegistrationFactory
from staff.tests.factories.batch_factory import BatchFactory
from staff.tests.factories.section_factory import SectionFactory

class EnrolmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Enrolment

    registration = factory.SubFactory(RegistrationFactory, batch=factory.SelfAttribute('..batch'))
    batch = factory.SubFactory(BatchFactory, swe_fundamentals=True)
    section = factory.SubFactory(SectionFactory, batch=factory.SelfAttribute('..batch'))
    student_user = factory.SubFactory(StudentUserFactory)
    status = Enrolment.ENROLLED

    class Params:
        coding_basics = factory.Trait(
            batch=factory.SubFactory(BatchFactory, coding_basics=True)
        )
        swe_fundamentals = factory.Trait(
            batch=factory.SubFactory(BatchFactory, swe_fundamentals=True),
        )

        coding_bootcamp = factory.Trait(
            batch=factory.SubFactory(BatchFactory, coding_bootcamp=True),
        )

        enrolled = factory.Trait(
            status=Enrolment.ENROLLED
        )
