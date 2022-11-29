from django.http import HttpResponseRedirect
from django.test import RequestFactory
from django.urls import reverse

from learn.views import home


def test_home_redirects_to_batch_list():
    request = RequestFactory().get(reverse('home'))

    response = home(request)

    assert response.status_code == HttpResponseRedirect.status_code
    assert reverse('home') in response.url
