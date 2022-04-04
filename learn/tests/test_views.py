from django.test import RequestFactory
from rest_framework import status
from rest_framework.test import APITestCase

from .. import views

class TestHomeView(APITestCase):
    def test_redirect_to_coding_basics(self):
        request = RequestFactory().get('')

        response = views.home(request)

        self.assertTrue(status.is_redirect(response.status_code))
        assert '/staff/coding_basics/' in response.url