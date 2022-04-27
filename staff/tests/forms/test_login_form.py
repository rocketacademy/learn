from django.contrib.auth import get_user_model
import pytest
from staff.forms import LoginForm

pytestmark = pytest.mark.django_db

class TestLoginForm:
    def test_empty_form_is_invalid(self):
        form = LoginForm(data={})

        outcome = form.is_valid()

        assert outcome is False, 'Should be invalid if no data provided'

    def test_form_without_password_is_invalid(self):
        user_email = 'someemail@domain.com'
        user_password = 'somepassword'

        User = get_user_model()
        User.objects.create_user(user_email, 'FirstName', 'LastName', user_password)

        form = LoginForm(
            data={
                'email': 'someemail@domain.com',
                'password': ''
            }
        )

        outcome = form.is_valid()

        assert outcome is False, 'Should be invalid if password not provided'
        assert 'password' in form.errors, 'Should have password field error'

    def test_form_with_inputs_is_valid(self):
        user_email = 'someemail@domain.com'
        user_password = 'somepassword'

        User = get_user_model()
        User.objects.create_user(user_email, 'FirstName', 'LastName', user_password)

        form = LoginForm(
            data={
                'email': user_email,
                'password': user_password
            }
        )

        outcome = form.is_valid()

        assert outcome is True, 'Should be valid if both inputs provided'
