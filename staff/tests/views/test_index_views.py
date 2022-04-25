from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from rest_framework import status
from rest_framework.test import APITestCase

from staff.views.index import index

class TestIndexView(APITestCase):
    def test_anonymous_user_redirected_to_login(self):
        request = RequestFactory().get('')
        request.user = AnonymousUser()

        response = index(request)

        self.assertTrue(status.is_redirect(response.status_code))
        assert 'staff/coding-basics/batches/' in response.url
