from django.test import Client, RequestFactory
from django.contrib.auth.models import AnonymousUser
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from staff.views import coding_basics_view

class TestCodingBasicsView(APITestCase):
    def test_anonymous_user_redirected_to_login(self):
        request = RequestFactory().get('/coding_basics/')
        request.user = AnonymousUser()

        response = coding_basics_view(request)

        self.assertTrue(status.is_redirect(response.status_code))
        assert 'staff/login/?next=/coding_basics/' in response.url

    def test_logged_in_user_can_access(self):
        User = get_user_model()
        logged_in_user = User.objects.create(email='user@domain.com', first_name='FirstName', last_name='LastName', password='password1234!')
        request = RequestFactory().get('/coding_basics/')
        request.user = logged_in_user

        response = coding_basics_view(request)

        self.assertTrue(status.is_success(response.status_code))