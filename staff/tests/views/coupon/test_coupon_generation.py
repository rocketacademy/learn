import csv
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse, HttpResponseRedirect
from django.test import Client, RequestFactory
from django.urls import reverse
import pytest

from staff.views.coupon import CsvUploadView

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

def test_coupon_generation_anonymous_user_redirected_to_login():
    request = RequestFactory().get('/coupons/csv-upload/')
    request.user = AnonymousUser()

    response = CsvUploadView.as_view()(request)

    assert response.status_code == HttpResponseRedirect.status_code
    assert 'staff/login/?next=/coupons/csv-upload/' in response.url

def test_coupon_generation_template_rendered_for_logged_in_user(logged_in_existing_user):
    response = client.get(reverse('coupon_coupon_generation'))

    assert response.status_code == HttpResponse.status_code
    assert 'coupon/coupon_generation.html' in (template.name for template in response.templates)

def test_coupon_generation_success_renders_page_with_list_of(logged_in_existing_user):
    test_file_path = "./staff/tests/forms/csv_files/correct_test_file.csv"
    csv_file = open(test_file_path, 'r')
    content = csv_file.read()
    uploaded_file = SimpleUploadedFile(name=csv_file.name, content=bytes(content, 'utf-8'), content_type="multipart/form-data")

    response = client.post(reverse('coupon_coupon_generation'), {'csv_file': uploaded_file})

    assert response.status_code == HttpResponse.status_code
    assert 'coupon/coupon_generation_success.html' in (template.name for template in response.templates)
    assert response.context['csv_rows'] == [{'first_name': 'tester', 'email': 'test1@test.com'}, {'first_name': 'tester2', 'email': 'test2@gmail.com'}]

def test_coupon_generation_no_upload_rerenders_form_page_with_appropriate_error_text(logged_in_existing_user):
    response = client.post(reverse('coupon_coupon_generation'))

    assert response.status_code == HttpResponse.status_code
    assert 'coupon/coupon_generation.html' in (template.name for template in response.templates)
    assert 'This field is required.' in response.context['errors'][0]

def test_coupon_generation_not_csv_rerenders_form_page_with_appropriate_error_text(logged_in_existing_user):
    uploaded_file = SimpleUploadedFile(name='test.txt', content=bytes('test content', 'utf-8'), content_type="multipart/form-data")

    response = client.post(reverse('coupon_coupon_generation'), {'csv_file': uploaded_file})

    assert response.status_code == HttpResponse.status_code
    assert 'coupon/coupon_generation.html' in (template.name for template in response.templates)
    assert 'The file you uploaded is not a .csv file!' in response.context['errors'][0]

def test_coupon_generation_incorrect_headers_rerenders_form_page_with_appropriate_error_text(logged_in_existing_user):
    test_file_path = "./staff/tests/forms/csv_files/incorrect_headers_test_file.csv"
    csv_file = open(test_file_path, 'r')
    content = csv_file.read()
    uploaded_file = SimpleUploadedFile(name=csv_file.name, content=bytes(content, 'utf-8'), content_type="multipart/form-data")

    response = client.post(reverse('coupon_coupon_generation'), {'csv_file': uploaded_file})
    print(response.context['errors'])

    assert response.status_code == HttpResponse.status_code
    assert 'coupon/coupon_generation.html' in (template.name for template in response.templates)
    assert 'The file you uploaded requires the specific headers "first_name" and "email"!' in response.context['errors'][0]
