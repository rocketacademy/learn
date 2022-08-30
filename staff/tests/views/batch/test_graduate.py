import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.test import Client, RequestFactory
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.urls import reverse
import pytest

from staff.models import Batch, Course, Section
from staff.views.batch import GraduateView

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
def batch():
    start_date = datetime.date.today() - datetime.timedelta(days=2)
    course = Course.objects.create(name=settings.CODING_BASICS)
    batch = Batch.objects.create(
        course=course,
        start_date=start_date,
        end_date=start_date + datetime.timedelta(days=1),
        capacity=90,
        sections=5
    )

    yield batch


def test_anonymous_user_redirected_to_login(batch):
    request = RequestFactory().get(f"/basics/batches/{batch.id}/graduate/")
    request.user = AnonymousUser()

    response = GraduateView.as_view()(request, batch.id)

    assert response.status_code == HttpResponseRedirect.status_code
    assert f"staff/login/?next=/basics/batches/{batch.id}/graduate/" in response.url

def test_logged_in_user_can_access(batch, existing_user):
    request = RequestFactory().get(f"/basics/batches/{batch.id}/graduate")
    request.user = existing_user

    response = GraduateView.as_view()(request, batch.id)

    assert response.status_code == HttpResponse.status_code

def test_template_rendered_if_batch_has_ended(batch, existing_user):
    client.post('/staff/login/', {'email': existing_user.email, 'password': 'password1234!'})

    response = client.get(reverse('batch_graduate', kwargs={'batch_id': batch.id}))

    assert response.status_code == HttpResponse.status_code
    assert 'basics/batch/graduate.html' in (template.name for template in response.templates)

def test_redirection_if_batch_has_not_ended(batch, existing_user):
    batch.end_date = datetime.date.today() + datetime.timedelta(days=1)
    batch.save()
    client.post('/staff/login/', {'email': existing_user.email, 'password': 'password1234!'})

    response = client.get(reverse('batch_graduate', kwargs={'batch_id': batch.id}))

    assert response.status_code == HttpResponseRedirect.status_code
