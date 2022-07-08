from django.test import Client
from django.urls import reverse
import pytest

pytestmark = pytest.mark.django_db


def test_coupon_new_template_rendered():
    response = Client().get(reverse('coupon_new'))

    assert 'coupon/new.html' in (template.name for template in response.templates)
