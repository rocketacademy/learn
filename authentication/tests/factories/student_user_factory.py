from django.conf import settings
import factory

from authentication.models import StudentUser


class StudentUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StudentUser

    email = 'studentuser@domain.com'
    first_name = 'FirstName'
    last_name = 'LastName'
    password = settings.PLACEHOLDER_PASSWORD
