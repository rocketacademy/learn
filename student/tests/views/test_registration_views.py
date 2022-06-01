import datetime
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseRedirect
from django.test import Client
from django.urls import reverse
import pytest

from staff.models import Batch, Course
from student.models.registration import Registration

pytestmark = pytest.mark.django_db
client = Client()
User = get_user_model()

existing_user_email = 'EXISTING_USER@EMAIL.COM'
existing_user_first_name = 'Existing'
existing_user_last_name = 'User'
existing_user_password = settings.PLACEHOLDER_PASSWORD

@pytest.fixture()
def batch():
    COURSE_NAME = settings.CODING_BASICS
    COURSE_DURATION_IN_DAYS = 35

    start_date = datetime.date.today()
    course = Course.objects.create(name=COURSE_NAME)
    batch = Batch.objects.create(
        course=course,
        start_date=start_date,
        end_date=start_date + datetime.timedelta(COURSE_DURATION_IN_DAYS),
        capacity=90,
        sections=5
    )

    yield batch

@pytest.fixture()
def existing_user():
    existing_user = User.objects.create(
        email=existing_user_email,
        first_name=existing_user_first_name,
        last_name=existing_user_last_name,
        password=existing_user_password
    )

    yield existing_user

def test_registration_wizard_form_existing_user(batch, existing_user):
    batch_selection_form_response = client.post(reverse('basics_register'), {
        'registration_wizard-current_step': 'batch_selection',
        'batch_selection-batch': '1',
    })
    student_info_form_response = client.post(reverse('basics_register'), {
        'registration_wizard-current_step': 'student_info',
        'student_info-first_name': existing_user_first_name,
        'student_info-last_name': existing_user_last_name,
        'student_info-email': existing_user_email,
        'student_info-country_of_residence': 'SG',
        'student_info-referral_channel': 'word_of_mouth',
    })

    assert batch_selection_form_response.status_code == HttpResponse.status_code
    assert student_info_form_response.status_code == HttpResponseRedirect.status_code
    registration = Registration.objects.get(email=existing_user_email)
    assert registration.batch == batch
    assert User.objects.all().count() == 1

def test_registration_wizard_form_new_user(batch, existing_user):
    client.post(reverse('basics_register'), {
        'registration_wizard-current_step': 'batch_selection',
        'batch_selection-batch': '1',
    })
    client.post(reverse('basics_register'), {
        'registration_wizard-current_step': 'student_info',
        'student_info-first_name': 'New',
        'student_info-last_name': 'User',
        'student_info-email': 'new_user@email.com',
        'student_info-country_of_residence': 'SG',
        'student_info-referral_channel': 'facebook',
    })

    assert User.objects.all().count() == 2
