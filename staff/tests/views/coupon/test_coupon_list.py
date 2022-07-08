from django.test import Client
from django.urls import reverse
import pytest

pytestmark = pytest.mark.django_db


def test_coupon_list_template_rendered():
    response = Client().get(reverse('coupon_list'))

    assert 'coupon/list.html' in (template.name for template in response.templates)
