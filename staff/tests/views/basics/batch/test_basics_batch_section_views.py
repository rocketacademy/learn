from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.test import Client, RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
import pytest

from staff.views.basics.basics_section import ListView

pytestmark = pytest.mark.django_db
client = Client()


def test_basics_batch_section_list_anonymous_user_redirected_to_login(coding_basics_batch):
    request = RequestFactory().get(f"/swe-fundamentals/batches/{coding_basics_batch.id}/sections/")
    request.user = AnonymousUser()

    response = ListView.as_view()(request)

    assert response.status_code == HttpResponseRedirect.status_code
    assert f"staff/login/?next=/swe-fundamentals/batches/{coding_basics_batch.id}/sections/" in response.url

def test_swe_fundamentals_batch_section_list_logged_in_user_can_access(swe_fundamentals_batch, existing_user):
    client.post('/staff/login/', {'email': existing_user.email, 'password': settings.PLACEHOLDER_PASSWORD})

    response = client.get(reverse('swe_fundamentals_batch_section_list', kwargs={'batch_id': swe_fundamentals_batch.id}))

    assert response.status_code == HttpResponse.status_code
    assert list(response.context['sections']) == list(swe_fundamentals_batch.section_set.all())
    assert 'basics/section/list.html' in (template.name for template in response.templates)

def test_basics_batch_section_list_logged_in_user_can_access(coding_basics_batch, existing_user):
    client.post('/staff/login/', {'email': existing_user.email, 'password': settings.PLACEHOLDER_PASSWORD})

    response = client.get(reverse('swe_fundamentals_batch_section_list', kwargs={'batch_id': coding_basics_batch.id}))

    assert response.status_code == HttpResponse.status_code
    assert list(response.context['sections']) == list(coding_basics_batch.section_set.all())
    assert 'basics/section/list.html' in (template.name for template in response.templates)

def test_swe_fundamentals_batch_section_detail_template_rendered_if_batch_and_sections_exists(enrolment_factory, existing_user):
    swe_fundamentals_enrolment = enrolment_factory(swe_fundamentals=True)
    swe_fundamentals_batch = swe_fundamentals_enrolment.batch
    first_section = swe_fundamentals_batch.section_set.first()
    client.post('/staff/login/', {'email': existing_user.email, 'password': settings.PLACEHOLDER_PASSWORD})

    response = client.get(
        reverse(
            'basics_batch_section_detail',
            kwargs={
                'batch_id': swe_fundamentals_batch.id,
                'section_id': first_section.id
            }
        )
    )

    assert response.status_code == HttpResponse.status_code
    assert response.context['batch'] == swe_fundamentals_batch
    assert list(response.context['batch_schedules']) == list(swe_fundamentals_batch.batchschedule_set.all())
    assert response.context['section'] == first_section
    assert list(response.context['students']) == [swe_fundamentals_batch.enrolment_set.first().student_user]
    assert response.context['current_tab'] == 'overview'
    assert 'basics/section/detail.html' in (template.name for template in response.templates)


def test_basics_batch_section_detail_template_rendered_if_batch_and_sections_exists(enrolment_factory, existing_user):
    coding_basics_enrolment = enrolment_factory(coding_basics=True)
    coding_basics_batch = coding_basics_enrolment.batch
    first_section = coding_basics_batch.section_set.first()
    client.post('/staff/login/', {'email': existing_user.email, 'password': settings.PLACEHOLDER_PASSWORD})

    response = client.get(
        reverse(
            'basics_batch_section_detail',
            kwargs={
                'batch_id': coding_basics_batch.id,
                'section_id': first_section.id
            }
        )
    )

    assert response.status_code == HttpResponse.status_code
    assert response.context['batch'] == coding_basics_batch
    assert list(response.context['batch_schedules']) == list(coding_basics_batch.batchschedule_set.all())
    assert response.context['section'] == first_section
    assert list(response.context['students']) == [coding_basics_batch.enrolment_set.first().student_user]
    assert response.context['current_tab'] == 'overview'
    assert 'basics/section/detail.html' in (template.name for template in response.templates)
