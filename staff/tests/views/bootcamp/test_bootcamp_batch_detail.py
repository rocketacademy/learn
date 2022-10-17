from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseRedirect
from django.test import Client, RequestFactory
from django.urls import reverse
import pytest

from staff.models import Section
from staff.views.bootcamp.bootcamp_batch import DetailView

pytestmark = pytest.mark.django_db
client = Client()

@pytest.fixture()
def existing_user():
    User = get_user_model()
    existing_user = User.objects.create_user(
        email='user@domain.com',
        first_name='FirstName',
        last_name='LastName',
        password='password1234!'
    )

    yield existing_user

@pytest.fixture()
def batch_with_section(batch_factory, course_factory):
    coding_bootcamp_course = course_factory(coding_bootcamp=True)
    coding_bootcamp_batch = batch_factory(course=coding_bootcamp_course)
    Section.objects.create(
        batch=coding_bootcamp_batch,
        number=1,
        capacity=18
    )

    yield coding_bootcamp_batch

def test_anonymous_user_redirected_to_login(batch_with_section):
    request = RequestFactory().get(f"/bootcamp/batches/{batch_with_section.id}/")
    request.user = AnonymousUser()

    response = DetailView.as_view()(request, batch_with_section.id)

    assert response.status_code == HttpResponseRedirect.status_code
    assert f"staff/login/?next=/bootcamp/batches/{batch_with_section.id}/" in response.url

def test_logged_in_user_can_access(batch_with_section, existing_user):
    request = RequestFactory().get(f"/bootcamp/batches/{batch_with_section.id}/")
    request.user = existing_user

    response = DetailView.as_view()(request, batch_with_section.id)

    assert response.status_code == HttpResponse.status_code

def test_template_rendered_if_batch_exists(batch_with_section, existing_user):
    client.post('/staff/login/', {'email': existing_user.email, 'password': 'password1234!'})

    response = client.get(reverse('bootcamp_batch_detail', kwargs={'batch_id': batch_with_section.id}))

    assert response.status_code == HttpResponse.status_code
    assert 'bootcamp/batch/detail.html' in (template.name for template in response.templates)
