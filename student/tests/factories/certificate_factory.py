from datetime import date
import factory

from staff.models import Certificate
from student.tests.factories.enrolment_factory import EnrolmentFactory


class CertificateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Certificate

    enrolment = factory.SubFactory(EnrolmentFactory, swe_fundamentals=True)
    graduation_date = date.today()

    class Params:
        swe_fundamentals = factory.Trait(
            enrolment=factory.SubFactory(EnrolmentFactory, swe_fundamentals=True)
        )
