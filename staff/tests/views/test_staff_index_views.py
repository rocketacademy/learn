from http.client import HTTPResponse
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect
from django.test import RequestFactory
from django.urls import reverse
from rest_framework.test import APITestCase

from staff.views.index import IndexView

class TestIndexView(APITestCase):
    def test_anonymous_user_redirected_to_login(self):
        request = RequestFactory().get('')
        request.user = AnonymousUser()

        response = IndexView.as_view()(request)

        assert response.status_code == HttpResponseRedirect.status_code
        assert response['location'] == reverse('batch_list')
