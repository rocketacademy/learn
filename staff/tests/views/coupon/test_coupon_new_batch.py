from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse, HttpResponseRedirect
from django.test import Client, RequestFactory
from django.urls import reverse
from unittest.mock import ANY
import pytest

from emails.library.sendgrid import Sendgrid
from payment.models import Coupon
from payment.models.coupon_effect import CouponEffect
from staff.models import Course
from staff.views.coupon import NewBatchView

pytestmark = pytest.mark.django_db
client = Client()


@pytest.fixture()
def logged_in_existing_user():
    User = get_user_model()
    existing_user = User.objects.create_user(
        email='user@domain.com',
        first_name='FirstName',
        last_name='LastName',
        password='password1234!'
    )
    client.post('/staff/login/', {'email': existing_user.email, 'password': 'password1234!'})

    yield logged_in_existing_user

@pytest.fixture()
def course_basics():
    course = Course.objects.create(name=settings.CODING_BASICS)
    yield course

@pytest.fixture()
def course_bootcamp():
    course = Course.objects.create(name=settings.CODING_BOOTCAMP)
    yield course

@pytest.fixture()
def coupon_effect_basics(course_basics):
    coupon_effect_basics = CouponEffect.objects.create(
        couponable_type=course_basics.__class__.__name__,
        couponable_id=course_basics.id,
        discount_type=CouponEffect.DOLLARS,
        discount_amount=20
    )
    yield coupon_effect_basics

@pytest.fixture()
def coupon_effect_bootcamp(course_bootcamp):
    coupon_effect_bootcamp = CouponEffect.objects.create(
        couponable_type=course_bootcamp.__class__.__name__,
        couponable_id=course_bootcamp.id,
        discount_type=CouponEffect.DOLLARS,
        discount_amount=200
    )
    yield coupon_effect_bootcamp


def test_coupon_generation_anonymous_user_redirected_to_login():
    request = RequestFactory().get('/coupons/csv-upload/')
    request.user = AnonymousUser()

    response = NewBatchView.as_view()(request)

    assert response.status_code == HttpResponseRedirect.status_code
    assert 'staff/login/?next=/coupons/csv-upload/' in response.url

def test_coupon_generation_template_rendered_for_logged_in_user(logged_in_existing_user):
    response = client.get(reverse('coupon_new_batch'))

    assert response.status_code == HttpResponse.status_code
    assert 'coupon/new_batch.html' in (template.name for template in response.templates)

def test_coupon_generation_success_redirects_page(mocker, logged_in_existing_user, course_basics, course_bootcamp):
    mocker.patch('emails.library.sendgrid.Sendgrid.send')
    test_file_path = "./staff/tests/forms/csv_files/correct_test_file.csv"
    csv_file = open(test_file_path, 'r')
    content = csv_file.read()
    uploaded_file = SimpleUploadedFile(name=csv_file.name, content=bytes(content, 'utf-8'), content_type="multipart/form-data")

    response = client.post(reverse('coupon_new_batch'), {'csv_file': uploaded_file})

    assert response.status_code == HttpResponseRedirect.status_code

def test_coupon_generation_no_upload_rerenders_form_page_with_appropriate_error_text(mocker, logged_in_existing_user):
    mocker.patch('emails.library.sendgrid.Sendgrid.send')
    response = client.post(reverse('coupon_new_batch'))

    assert response.status_code == HttpResponse.status_code
    assert 'coupon/new_batch.html' in (template.name for template in response.templates)
    assert 'This field is required.' in response.context['errors'][0]

def test_coupon_generation_not_csv_rerenders_form_page_with_appropriate_error_text(mocker, logged_in_existing_user):
    mocker.patch('emails.library.sendgrid.Sendgrid.send')
    uploaded_file = SimpleUploadedFile(name='test.txt', content=bytes('test content', 'utf-8'), content_type="multipart/form-data")

    response = client.post(reverse('coupon_new_batch'), {'csv_file': uploaded_file})

    assert response.status_code == HttpResponse.status_code
    assert 'coupon/new_batch.html' in (template.name for template in response.templates)
    assert 'The file you uploaded is not a .csv file!' in response.context['errors'][0]

def test_coupon_generation_incorrect_headers_rerenders_form_page_with_appropriate_error_text(mocker, logged_in_existing_user):
    mocker.patch('emails.library.sendgrid.Sendgrid.send')
    test_file_path = "./staff/tests/forms/csv_files/incorrect_headers_test_file.csv"
    csv_file = open(test_file_path, 'r')
    content = csv_file.read()
    uploaded_file = SimpleUploadedFile(name=csv_file.name, content=bytes(content, 'utf-8'), content_type="multipart/form-data")

    response = client.post(reverse('coupon_new_batch'), {'csv_file': uploaded_file})

    assert response.status_code == HttpResponse.status_code
    assert 'coupon/new_batch.html' in (template.name for template in response.templates)
    assert 'The file you uploaded requires the specific headers "first_name" and "email"!' in response.context['errors'][0]

def test_coupon_generation_creates_correct_coupons(mocker, logged_in_existing_user, coupon_effect_basics, coupon_effect_bootcamp):
    mocker.patch('emails.library.sendgrid.Sendgrid.send')
    test_file_path = "./staff/tests/forms/csv_files/correct_test_file.csv"
    csv_file = open(test_file_path, 'r')
    content = csv_file.read()
    uploaded_file = SimpleUploadedFile(name=csv_file.name, content=bytes(content, 'utf-8'), content_type="multipart/form-data")

    client.post(reverse('coupon_new_batch'), {'csv_file': uploaded_file})
    test_coupon = Coupon.objects.first()
    test_coupon_effects = list(test_coupon.effects.all())

    assert Coupon.objects.count() == 2
    assert test_coupon_effects == [coupon_effect_basics, coupon_effect_bootcamp]
    assert test_coupon.description == 'test1@test.com'

def test_send_cooupon_email_batch(mocker, logged_in_existing_user, course_basics, course_bootcamp):
    mocker.patch('emails.library.sendgrid.Sendgrid.send')
    test_file_path = "./staff/tests/forms/csv_files/correct_test_file.csv"
    csv_file = open(test_file_path, 'r')
    content = csv_file.read()
    uploaded_file = SimpleUploadedFile(name=csv_file.name, content=bytes(content, 'utf-8'), content_type="multipart/form-data")

    client.post(reverse('coupon_new_batch'), {'csv_file': uploaded_file})
    coupon = Coupon.objects.last()

    Sendgrid.send.assert_called_with(
        coupon.id,
        type(coupon).__name__,
        'community@rocketacademy.co',
        'test2@test.com',
        settings.COUPON_CODE_NOTIFICATION_TEMPLATE_ID,
        # Using ANY because cannot recreate sendgrid.helper.mail object
        ANY
    )
    Sendgrid.send.call_count == 2
