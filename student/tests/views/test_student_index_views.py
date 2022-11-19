from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from rest_framework import status
from rest_framework.test import APITestCase

from student.views.index import IndexView

class TestIndexView(APITestCase):
    def test_user_redirected_to_registration_form(self):
        request = RequestFactory().get('')
        request.user = AnonymousUser()

        response = IndexView.as_view()(request)

        self.assertTrue(status.is_redirect(response.status_code))
        assert 'student/courses/swe-fundamentals/register/' in response.url
