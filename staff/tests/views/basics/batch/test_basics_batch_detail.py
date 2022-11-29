from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse, HttpResponseRedirect
from django.test import Client, RequestFactory
from django.urls import reverse
import pytest

from staff.views.basics.basics_batch import DetailView

pytestmark = pytest.mark.django_db
client = Client()


def test_anonymous_user_redirected_to_login(coding_basics_batch):
    request = RequestFactory().get(f"/swe-fundamentals/batches/{coding_basics_batch.id}/")
    request.user = AnonymousUser()

    response = DetailView.as_view()(request, coding_basics_batch.id)

    assert response.status_code == HttpResponseRedirect.status_code
    assert f"staff/login/?next=/swe-fundamentals/batches/{coding_basics_batch.id}/" in response.url

def test_template_rendered_with_context_if_batch_exists(coding_basics_batch, existing_user):
    client.post('/staff/login/', {'email': existing_user.email, 'password': settings.PLACEHOLDER_PASSWORD})

    response = client.get(reverse('swe_fundamentals_batch_detail', kwargs={'batch_id': coding_basics_batch.id}))

    assert response.status_code == HttpResponse.status_code
    assert response.context['current_tab'] == 'overview'
    assert response.context['batch'] == coding_basics_batch
    assert response.context['section_capacity'] == coding_basics_batch.section_set.first().capacity
    assert list(response.context['batch_schedules']) == list(coding_basics_batch.batchschedule_set.all())
    assert 'basics/batch/detail.html' in (template.name for template in response.templates)
