from django.http import HttpResponse, HttpResponseRedirect
from django.test import Client
from django.urls import reverse
import pytest

client = Client()
pytestmark = pytest.mark.django_db


def test_get_basics_certificate_detail_redirects_to_certificate_detail(certificate_factory):
    swe_fundamentals_certificate = certificate_factory(swe_fundamentals=True)

    response = client.get(
        reverse(
            'basics_certificate_detail',
            kwargs={'certificate_credential': swe_fundamentals_certificate.credential}
        )
    )

    assert response.status_code == HttpResponseRedirect.status_code
    assert response['location'] == reverse(
        'certificate_detail',
        kwargs={'certificate_credential': swe_fundamentals_certificate.credential}
    )

def test_get_detail_renders_certificate_if_exists(certificate_factory):
    swe_fundamentals_certificate = certificate_factory(swe_fundamentals=True)

    response = client.get(
        reverse(
            'certificate_detail',
            kwargs={'certificate_credential': swe_fundamentals_certificate.credential}
        )
    )

    assert response.status_code == HttpResponse.status_code
    assert response.context['certificate'] == swe_fundamentals_certificate
    assert 'certificate/detail.html' in (template.name for template in response.templates)

def test_get_detail_renders_error_if_certificate_does_not_exist():
    incorrect_credential = 'ABCDEF'

    response = client.get(
        reverse(
            'certificate_detail',
            kwargs={'certificate_credential': incorrect_credential}
        )
    )

    assert response.status_code == HttpResponse.status_code
    assert response.context['certificate_credential'] == incorrect_credential
    assert 'certificate/error.html' in (template.name for template in response.templates)
