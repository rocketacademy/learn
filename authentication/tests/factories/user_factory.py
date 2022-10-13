from django.conf import settings
from django.contrib.auth import get_user_model
import factory

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = 'user@domain.com'
    first_name = 'FirstName'
    last_name = 'LastName'
    password = settings.PLACEHOLDER_PASSWORD
