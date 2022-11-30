from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse, HttpResponseRedirect
from django.test import Client, RequestFactory
from django.urls import reverse
from unittest.mock import ANY
import pytest

from emails.library.sendgrid import Sendgrid
from payment.models import Coupon
from staff.views.coupon import NewBatchView

pytestmark = pytest.mark.django_db
client = Client()


def test_coupon_generation_anonymous_user_redirected_to_login():
    request = RequestFactory().get('/coupons/csv-upload/')
    request.user = AnonymousUser()

    response = NewBatchView.as_view()(request)

    assert response.status_code == HttpResponseRedirect.status_code
    assert 'staff/login/?next=/coupons/csv-upload/' in response.url

def test_coupon_generation_template_rendered_for_logged_in_user(existing_user):
    client.post('/staff/login/', {'email': existing_user.email, 'password': settings.PLACEHOLDER_PASSWORD})

    response = client.get(reverse('coupon_new_batch'))

    assert response.status_code == HttpResponse.status_code
    assert 'coupon/new_batch.html' in (template.name for template in response.templates)

def test_coupon_generation_success_redirects_page(mocker, existing_user, swe_fundamentals_coupon_effect, coding_bootcamp_coupon_effect):
    mocker.patch('emails.library.sendgrid.Sendgrid.send')
    test_file_path = "./staff/tests/forms/csv_files/correct_test_file.csv"
    csv_file = open(test_file_path, 'r')
    content = csv_file.read()
    uploaded_file = SimpleUploadedFile(name=csv_file.name, content=bytes(content, 'utf-8'), content_type="multipart/form-data")
    client.post('/staff/login/', {'email': existing_user.email, 'password': settings.PLACEHOLDER_PASSWORD})

    response = client.post(reverse('coupon_new_batch'), {'csv_file': uploaded_file})

    assert response.status_code == HttpResponseRedirect.status_code

def test_coupon_generation_no_upload_rerenders_form_page_with_appropriate_error_text(mocker, existing_user):
    mocker.patch('emails.library.sendgrid.Sendgrid.send')
    client.post('/staff/login/', {'email': existing_user.email, 'password': settings.PLACEHOLDER_PASSWORD})

    response = client.post(reverse('coupon_new_batch'))

    assert response.status_code == HttpResponse.status_code
    assert 'coupon/new_batch.html' in (template.name for template in response.templates)
    assert 'This field is required.' in response.context['errors'][0]

def test_coupon_generation_not_csv_rerenders_form_page_with_appropriate_error_text(mocker, existing_user):
    mocker.patch('emails.library.sendgrid.Sendgrid.send')
    uploaded_file = SimpleUploadedFile(name='test.txt', content=bytes('test content', 'utf-8'), content_type="multipart/form-data")
    client.post('/staff/login/', {'email': existing_user.email, 'password': settings.PLACEHOLDER_PASSWORD})

    response = client.post(reverse('coupon_new_batch'), {'csv_file': uploaded_file})

    assert response.status_code == HttpResponse.status_code
    assert 'coupon/new_batch.html' in (template.name for template in response.templates)
    assert 'The file you uploaded is not a .csv file!' in response.context['errors'][0]

def test_coupon_generation_incorrect_headers_rerenders_form_page_with_appropriate_error_text(mocker, existing_user):
    mocker.patch('emails.library.sendgrid.Sendgrid.send')
    test_file_path = "./staff/tests/forms/csv_files/incorrect_headers_test_file.csv"
    csv_file = open(test_file_path, 'r')
    content = csv_file.read()
    uploaded_file = SimpleUploadedFile(name=csv_file.name, content=bytes(content, 'utf-8'), content_type="multipart/form-data")
    client.post('/staff/login/', {'email': existing_user.email, 'password': settings.PLACEHOLDER_PASSWORD})

    response = client.post(reverse('coupon_new_batch'), {'csv_file': uploaded_file})

    assert response.status_code == HttpResponse.status_code
    assert 'coupon/new_batch.html' in (template.name for template in response.templates)
    assert 'The file you uploaded requires the specific headers "first_name" and "email"!' in response.context['errors'][0]

def test_coupon_generation_creates_correct_coupons(mocker, existing_user, swe_fundamentals_coupon_effect, coding_bootcamp_coupon_effect):
    mocker.patch('emails.library.sendgrid.Sendgrid.send')
    test_file_path = "./staff/tests/forms/csv_files/correct_test_file.csv"
    csv_file = open(test_file_path, 'r')
    content = csv_file.read()
    uploaded_file = SimpleUploadedFile(name=csv_file.name, content=bytes(content, 'utf-8'), content_type="multipart/form-data")
    client.post('/staff/login/', {'email': existing_user.email, 'password': settings.PLACEHOLDER_PASSWORD})

    client.post(reverse('coupon_new_batch'), {'csv_file': uploaded_file})
    test_coupon = Coupon.objects.first()
    test_coupon_effects = list(test_coupon.effects.all())

    assert Coupon.objects.count() == 2
    assert test_coupon_effects == [swe_fundamentals_coupon_effect, coding_bootcamp_coupon_effect]
    assert test_coupon.description == 'test1@test.com'

def test_send_cooupon_email_batch(mocker, existing_user, swe_fundamentals_coupon_effect, coding_bootcamp_coupon_effect):
    mocker.patch('emails.library.sendgrid.Sendgrid.send_bulk')
    test_file_path = "./staff/tests/forms/csv_files/correct_test_file.csv"
    csv_file = open(test_file_path, 'r')
    content = csv_file.read()
    uploaded_file = SimpleUploadedFile(name=csv_file.name, content=bytes(content, 'utf-8'), content_type="multipart/form-data")
    client.post('/staff/login/', {'email': existing_user.email, 'password': settings.PLACEHOLDER_PASSWORD})

    client.post(reverse('coupon_new_batch'), {'csv_file': uploaded_file})

    Sendgrid.send_bulk.assert_called_once_with(
        'community@rocketacademy.co',
        [ANY, ANY],
        settings.COUPON_CODE_NOTIFICATION_TEMPLATE_ID
    )
