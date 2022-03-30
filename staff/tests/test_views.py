from django.test import Client, RequestFactory
from django.contrib.auth.models import AnonymousUser
from rest_framework import status
from rest_framework.test import APITestCase
from mixer.backend.django import mixer
from django.contrib.auth import get_user_model

from .. import views

class TestIndexView(APITestCase):
    def test_anonymous_user_redirected_to_login(self):
        request = RequestFactory().get('')
        request.user = AnonymousUser()

        response = views.index(request)

        self.assertTrue(status.is_redirect(response.status_code))
        assert 'staff/login/' in response.url

class TestLoginView(APITestCase):
    def test_anonymous_user_sees_login_form(self):
        request = RequestFactory().get('/login/')
        request.user = AnonymousUser()
        
        response = views.login_view(request)

        self.assertTrue(status.is_success(response.status_code))

    def test_existing_user_redirected_to_coding_basics_after_login(self):
        user_email = 'user@domain.com'
        user_password = 'password1234!'
        User = get_user_model()
        User.objects.create_user(user_email, 'FirstName', 'LastName', user_password)
        
        response = Client().post('/staff/login/', {'email': user_email, 'password': user_password})

        self.assertTrue(status.is_redirect(response.status_code))
        assert 'staff/coding_basics/' in response.url

    def test_form_rendered_again_if_password_incorrect(self):
        user_email = 'user@domain.com'
        user_password = 'password1234!'
        incorrect_password = 'incorrectpassword'
        User = get_user_model()
        User.objects.create_user(user_email, 'FirstName', 'LastName', user_password)

        response = Client().post('/staff/login/', {'email': user_email, 'password': incorrect_password})

        self.assertTrue(status.is_success(response.status_code))
        self.assertTemplateUsed(response, 'login.html')

class TestCodingBasicsView(APITestCase):
    def test_anonymous_user_redirected_to_login(self):
        request = RequestFactory().get('/coding_basics/')
        request.user = AnonymousUser()
        
        response = views.coding_basics_view(request)

        self.assertTrue(status.is_redirect(response.status_code))
        assert 'staff/login/?next=/coding_basics/' in response.url

    def test_logged_in_user(self):
        logged_in_user = mixer.blend('authentication.User')
        request = RequestFactory().get('/coding_basics/')
        request.user = logged_in_user

        response = views.coding_basics_view(request)

        self.assertTrue(status.is_success(response.status_code))