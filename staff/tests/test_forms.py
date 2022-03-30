import pytest
from django.contrib.auth import get_user_model
from .. import forms

pytestmark = pytest.mark.django_db

class TestLoginForm:
    def test_empty_form_is_invalid(self):
        form = forms.LoginForm(data={})

        outcome = form.is_valid()

        assert outcome == False, 'Should be invalid if no data provided'

    def test_form_without_password_is_invalid(self):
        user_email = 'someemail@domain.com'
        user_password = 'somepassword'

        User = get_user_model()
        User.objects.create_user(user_email, 'FirstName', 'LastName', user_password)

        form = forms.LoginForm(
            data={
                'email': 'someemail@domain.com',
                'password': ''
            }
        )

        outcome = form.is_valid()

        assert outcome == False, 'Should be invalid if password not provided'
        assert 'password' in form.errors, 'Should have password field error'

    def test_form_with_inputs_is_valid(self):
        user_email = 'someemail@domain.com'
        user_password = 'somepassword'

        User = get_user_model()
        User.objects.create_user(user_email, 'FirstName', 'LastName', user_password)

        form = forms.LoginForm(
            data={
                'email': user_email,
                'password': user_password
            }
        )

        outcome = form.is_valid()

        assert outcome == True, 'Should be valid if both inputs provided'