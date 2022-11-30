from datetime import date, timedelta
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse, HttpResponseRedirect
from django.test import Client, RequestFactory
from django.urls import reverse
import pytest

from emails.library.sendgrid import Sendgrid
from payment.models import ReferralCoupon
from staff.models import Certificate
from staff.views.course.swe_fundamentals.swe_fundamentals_batch import GraduateView
from student.models.enrolment import Enrolment

pytestmark = pytest.mark.django_db
client = Client()


def test_get_anonymous_user_redirected_to_login(batch_factory):
    batch = batch_factory()
    request = RequestFactory().get(f"/courses/swe-fundamentals/batches/{batch.id}/graduate/")
    request.user = AnonymousUser()

    response = GraduateView.as_view()(request, batch.id)

    assert response.status_code == HttpResponseRedirect.status_code
    assert f"staff/login/?next=/courses/swe-fundamentals/batches/{batch.id}/graduate/" in response.url

def test_get_template_rendered_if_batch_has_ended(enrolment_factory, existing_user):
    swe_fundamentals_enrolment = enrolment_factory(swe_fundamentals=True)
    swe_fundamentals_batch = swe_fundamentals_enrolment.batch
    swe_fundamentals_batch.start_date = date.today() - timedelta(days=2)
    swe_fundamentals_batch.end_date = date.today() - timedelta(days=1)
    swe_fundamentals_batch.save()
    client.post('/staff/login/', {'email': existing_user.email, 'password': settings.PLACEHOLDER_PASSWORD})

    response = client.get(reverse('swe_fundamentals_batch_graduate', kwargs={'batch_id': swe_fundamentals_batch.id}))

    assert response.status_code == HttpResponse.status_code
    assert 'course/swe_fundamentals/batch/graduate.html' in (template.name for template in response.templates)

def test_get_redirection_if_batch_has_not_ended(enrolment_factory, existing_user):
    swe_fundamentals_enrolment = enrolment_factory(swe_fundamentals=True)
    swe_fundamentals_batch = swe_fundamentals_enrolment.batch
    client.post('/staff/login/', {'email': existing_user.email, 'password': settings.PLACEHOLDER_PASSWORD})

    response = client.get(reverse('swe_fundamentals_batch_graduate', kwargs={'batch_id': swe_fundamentals_batch.id}))

    assert response.status_code == HttpResponseRedirect.status_code

def test_post_updates_enrolment_statuses_and_sends_emails(
    mocker,
    enrolment_factory,
    existing_user,
    swe_fundamentals_coupon_effect,
    coding_bootcamp_coupon_effect
):
    swe_fundamentals_enrolment = enrolment_factory(swe_fundamentals=True)
    swe_fundamentals_batch = swe_fundamentals_enrolment.batch
    client.post('/staff/login/', {'email': existing_user.email, 'password': settings.PLACEHOLDER_PASSWORD})
    mocker.patch('emails.library.sendgrid.Sendgrid.send_bulk')

    response = client.post(
        reverse(
            'swe_fundamentals_batch_graduate',
            kwargs={'batch_id': swe_fundamentals_batch.id}
        ),
        data={
            'enrolment': [
                swe_fundamentals_enrolment.id,
            ]
        }
    )

    swe_fundamentals_enrolment.refresh_from_db()
    certificate = Certificate.objects.first()
    referral_coupon = ReferralCoupon.objects.first()
    assert swe_fundamentals_enrolment.status == Enrolment.PASSED
    assert certificate.enrolment == swe_fundamentals_enrolment
    assert referral_coupon.referrer.email == swe_fundamentals_enrolment.student_user.email
    assert list(referral_coupon.effects.all()) == [swe_fundamentals_coupon_effect, coding_bootcamp_coupon_effect]
    Sendgrid.send_bulk.assert_called_once_with(
        settings.ROCKET_EDUCATION_EMAIL,
        [
            mocker.ANY,
        ],
        settings.CODING_BASICS_GRADUATION_NOTIFICATION_TEMPLATE_ID
    )
    assert response.status_code == HttpResponseRedirect.status_code
