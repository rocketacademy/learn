from django.conf import settings
from django.contrib.auth import get_user_model
import pytest

User = get_user_model()
pytestmark = pytest.mark.django_db

email = 'someemail@domain.com'
first_name = 'FirstName'
last_name = 'LastName'
password = settings.PLACEHOLDER_PASSWORD


class TestUserManager:
    def test_empty_email_does_not_create_user(self):
        email = ''

        with pytest.raises(ValueError) as exception_info:
            User.objects.create_user(
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password
            )

        assert str(exception_info.value) == 'User must have an email address.'

class TestUser:
    def test_model_create(self):
        user = User.objects.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password
        )

        assert user.email == email
        assert user.first_name == first_name.upper()
        assert user.last_name == last_name.upper()
        assert user.password is not None

    def test_full_name(self):
        user = User.objects.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password
        )

        full_name = user.full_name()

        assert full_name == f'{first_name.capitalize()} {last_name.capitalize()}'
