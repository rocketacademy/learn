from datetime import date, timedelta
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse, HttpResponseRedirect
from django.test import Client, RequestFactory
from django.urls import reverse
import pytest

from authentication.models import StudentUser
from emails.library.sendgrid import Sendgrid
from payment.models import CouponEffect, ReferralCoupon
from staff.models import Certificate, Course, Section
from staff.views.course.swe_fundamentals.swe_fundamentals_batch import GraduateView
from student.models.enrolment import Enrolment
from student.models.registration import Registration

pytestmark = pytest.mark.django_db
client = Client()


def test_get_anonymous_user_redirected_to_login(batch_factory):
    batch = batch_factory()
    request = RequestFactory().get(f"/basics/batches/{batch.id}/graduate/")
    request.user = AnonymousUser()

    response = GraduateView.as_view()(request, batch.id)

    assert response.status_code == HttpResponseRedirect.status_code
    assert f"staff/login/?next=/basics/batches/{batch.id}/graduate/" in response.url

def test_get_template_rendered_if_batch_is_ready_for_graduation(batch_factory, existing_user):
    email = 'studentname@example.com'
    first_name = 'Student'
    last_name = 'Name'
    batch = batch_factory.create(
        start_date=date.today() - timedelta(days=2),
        end_date=date.today() - timedelta(days=1),
    )
    section = Section.objects.create(
        batch=batch,
        number=1,
        capacity=1
    )
    registration = Registration.objects.create(
        course=batch.course,
        batch=batch,
        first_name=first_name,
        last_name=last_name,
        email=email,
        country_of_residence='SG',
        referral_channel='word_of_mouth'
    )
    student_user = StudentUser.objects.create_user(
        email=email,
        first_name=first_name,
        last_name=last_name,
        password=settings.PLACEHOLDER_PASSWORD
    )
    Enrolment.objects.create(
        registration=registration,
        batch=batch,
        section=section,
        student_user=student_user
    )
    client.post('/staff/login/', {'email': existing_user.email, 'password': settings.PLACEHOLDER_PASSWORD})

    response = client.get(reverse('basics_batch_graduate', kwargs={'batch_id': batch.id}))

    assert response.status_code == HttpResponse.status_code
    assert 'course/swe_fundamentals/batch/graduate.html' in (template.name for template in response.templates)

def test_get_redirection_if_batch_is_not_ready_for_graduation(batch_factory, existing_user):
    batch = batch_factory()
    client.post('/staff/login/', {'email': existing_user.email, 'password': settings.PLACEHOLDER_PASSWORD})

    response = client.get(reverse('basics_batch_graduate', kwargs={'batch_id': batch.id}))

    assert response.status_code == HttpResponseRedirect.status_code

def test_post_updates_enrolment_statuses_and_sends_emails(mocker, batch_factory, course_factory, existing_user):
    batch = batch_factory()
    section = Section.objects.create(
        batch=batch,
        number=1,
        capacity=2
    )
    first_student_user = StudentUser.objects.create_user(
        first_name='First',
        last_name='Student',
        email='firststudent@example.com',
        password=settings.PLACEHOLDER_PASSWORD
    )
    first_registration = Registration.objects.create(
        course=batch.course,
        batch=batch,
        first_name=first_student_user.first_name,
        last_name=first_student_user.last_name,
        email=first_student_user.email,
        country_of_residence='SG',
        referral_channel='word_of_mouth'
    )
    first_enrolment = Enrolment.objects.create(
        registration=first_registration,
        batch=batch,
        section=section,
        student_user=first_student_user,
        status=Enrolment.ENROLLED
    )
    second_student_user = StudentUser.objects.create_user(
        first_name='Second',
        last_name='Student',
        email='secondstudent@example.com',
        password=settings.PLACEHOLDER_PASSWORD
    )
    second_registration = Registration.objects.create(
        course=batch.course,
        batch=batch,
        first_name=second_student_user.first_name,
        last_name=second_student_user.last_name,
        email=second_student_user.email,
        country_of_residence='SG',
        referral_channel='word_of_mouth'
    )
    second_enrolment = Enrolment.objects.create(
        registration=second_registration,
        batch=batch,
        section=section,
        student_user=second_student_user,
        status=Enrolment.ENROLLED
    )
    coding_basics_course = batch.course
    coding_bootcamp_course = course_factory.create(name=Course.CODING_BOOTCAMP)
    basics_coupon_effect = CouponEffect.objects.create(
        couponable_type=type(coding_basics_course).__name__,
        couponable_id=coding_basics_course.id,
        discount_type=CouponEffect.DOLLARS,
        discount_amount=20
    )
    bootcamp_coupon_effect = CouponEffect.objects.create(
        couponable_type=type(coding_bootcamp_course).__name__,
        couponable_id=coding_bootcamp_course.id,
        discount_type=CouponEffect.DOLLARS,
        discount_amount=200
    )
    client.post('/staff/login/', {'email': existing_user.email, 'password': settings.PLACEHOLDER_PASSWORD})
    mocker.patch('emails.library.sendgrid.Sendgrid.send_bulk')

    response = client.post(
        reverse(
            'basics_batch_graduate',
            kwargs={'batch_id': batch.id}
        ),
        data={
            'enrolment': [
                first_enrolment.id,
                second_enrolment.id
            ]
        }
    )

    first_enrolment.refresh_from_db()
    second_enrolment.refresh_from_db()
    first_certificate = Certificate.objects.first()
    second_certificate = Certificate.objects.last()
    first_referral_coupon = ReferralCoupon.objects.first()
    second_referral_coupon = ReferralCoupon.objects.last()
    assert first_enrolment.status == Enrolment.PASSED
    assert second_enrolment.status == Enrolment.PASSED
    assert first_certificate.enrolment == first_enrolment
    assert second_certificate.enrolment == second_enrolment
    assert first_referral_coupon.referrer.email == first_enrolment.student_user.email
    assert list(first_referral_coupon.effects.all()) == [basics_coupon_effect, bootcamp_coupon_effect]
    assert second_referral_coupon.referrer.email == second_enrolment.student_user.email
    assert list(second_referral_coupon.effects.all()) == [basics_coupon_effect, bootcamp_coupon_effect]
    Sendgrid.send_bulk.assert_called_once_with(
        settings.ROCKET_EDUCATION_EMAIL,
        [
            mocker.ANY,
            mocker.ANY,
        ],
        settings.CODING_BASICS_GRADUATION_NOTIFICATION_TEMPLATE_ID
    )
    assert response.status_code == HttpResponseRedirect.status_code
