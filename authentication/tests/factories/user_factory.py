from django.conf import settings
from django.contrib.auth import get_user_model
import factory
from faker import Faker

fake = Faker()
Faker.seed(0)
User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('email',)

    email = factory.LazyAttribute(lambda su: f"{su.first_name.lower()}{su.last_name.lower()}@example.com")
    first_name = fake.first_name()
    last_name = fake.last_name()
    password = settings.PLACEHOLDER_PASSWORD

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        manager = cls._get_manager(model_class)

        return manager.create_user(*args, **kwargs)
