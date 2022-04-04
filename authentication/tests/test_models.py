import pytest
from django.contrib.auth import get_user_model

User = get_user_model()
pytestmark = pytest.mark.django_db

email = 'someemail@domain.com'
first_name = 'FirstName'
last_name = 'LastName'
password = 'password1234!'

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
        
        assert str(exception_info.value) == 'User must have an email address.', 'Should raise ValueError with message if email was not provided'

class TestUser:
    def test_modeL_create(self):
        user = User.objects.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password
        )

        assert user.email == email, 'Should save email when creating instance of User'
        assert user.first_name == first_name.upper(), 'Should save first name in uppercase when creating instance of User'
        assert user.last_name == last_name.upper(), 'Should save last name in uppercase when creating instance of User'
        assert user.password is not None, 'Should save password when creating instance of User'

    def test_full_name(self):
        user = User.objects.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password
        )

        full_name = user.full_name()

        assert full_name == f'{first_name.upper()} {last_name.upper()}', 'Should return concatenated first and last names in uppercase'