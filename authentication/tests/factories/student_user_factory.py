from django.conf import settings
import factory
from faker import Faker

from authentication.models import StudentUser

fake = Faker()
Faker.seed(0)

class StudentUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StudentUser
        django_get_or_create = ('email',)

    email = factory.LazyAttribute(lambda su: f"{su.first_name.lower()}{su.last_name.lower()}@example.com")
    first_name = fake.first_name()
    last_name = fake.last_name()
    password = settings.PLACEHOLDER_PASSWORD
    hubspot_contact_id = None
