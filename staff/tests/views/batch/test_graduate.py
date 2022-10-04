import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.test import Client, RequestFactory
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.urls import reverse
import pytest

from authentication.models import StudentUser
from emails.library.sendgrid import Sendgrid
from payment.models import CouponEffect, ReferralCoupon
from staff.models import Batch, Certificate, Course, Section
from staff.views.batch import GraduateView
from student.models.enrolment import Enrolment
from student.models.registration import Registration

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
    course = Course.objects.create(name=Course.CODING_BASICS)
    batch = Batch.objects.create(
        course=course,
        start_date=start_date,
        end_date=start_date + datetime.timedelta(days=1),
        capacity=90,
        sections=5
    )

    yield batch

@pytest.fixture()
def batch_ready_for_graduation():
    email = 'studentname@example.com'
    first_name = 'Student'
    last_name = 'Name'
    start_date = datetime.date.today() - datetime.timedelta(days=2)
    coding_basics_course = Course.objects.create(name=Course.CODING_BASICS)
    batch = Batch.objects.create(
        course=coding_basics_course,
        start_date=start_date,
        end_date=start_date + datetime.timedelta(days=1),
        capacity=90,
        sections=5
    )
    section = Section.objects.create(
        batch=batch,
        number=1,
        capacity=1
    )
    registration = Registration.objects.create(
        course=coding_basics_course,
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

    yield batch

def test_get_anonymous_user_redirected_to_login(batch):
    request = RequestFactory().get(f"/basics/batches/{batch.id}/graduate/")
    request.user = AnonymousUser()

    response = GraduateView.as_view()(request, batch.id)

    assert response.status_code == HttpResponseRedirect.status_code
    assert f"staff/login/?next=/basics/batches/{batch.id}/graduate/" in response.url

def test_get_logged_in_user_can_access(batch, existing_user):
    request = RequestFactory().get(f"/basics/batches/{batch.id}/graduate")
    request.user = existing_user

    response = GraduateView.as_view()(request, batch.id)

    assert response.status_code == HttpResponseRedirect.status_code

def test_get_template_rendered_if_batch_is_ready_for_graduation(batch_ready_for_graduation, existing_user):
    client.post('/staff/login/', {'email': existing_user.email, 'password': 'password1234!'})

    response = client.get(reverse('batch_graduate', kwargs={'batch_id': batch_ready_for_graduation.id}))

    assert response.status_code == HttpResponse.status_code
    assert 'basics/batch/graduate.html' in (template.name for template in response.templates)

def test_get_redirection_if_batch_is_not_ready_for_graduation(batch, existing_user):
    batch.end_date = datetime.date.today() + datetime.timedelta(days=1)
    batch.save()
    client.post('/staff/login/', {'email': existing_user.email, 'password': 'password1234!'})

    response = client.get(reverse('batch_graduate', kwargs={'batch_id': batch.id}))

    assert response.status_code == HttpResponseRedirect.status_code

def test_post_updates_enrolment_statuses_and_sends_emails(mocker, batch, existing_user):
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
    coding_bootcamp_course = Course.objects.create(name=Course.CODING_BOOTCAMP)
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
    client.post('/staff/login/', {'email': existing_user.email, 'password': 'password1234!'})
    mocker.patch('emails.library.sendgrid.Sendgrid.send_bulk')

    response = client.post(
        reverse(
            'batch_graduate',
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
        settings.ROCKET_CODING_BASICS_EMAIL,
        [
            mocker.ANY,
            mocker.ANY,
        ],
        settings.CODING_BASICS_GRADUATION_NOTIFICATION_TEMPLATE_ID
    )
    assert response.status_code == HttpResponseRedirect.status_code
