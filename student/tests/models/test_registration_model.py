import datetime
from django.conf import settings
import pytest
from unittest.mock import patch

from authentication.models import StudentUser
from payment.models import StripePayment
from staff.models.batch import Batch
from staff.models.course import Course
from staff.models.section import Section
from student.models.enrolment import Enrolment
from student.models.registration import (
    Registration,
    record_stripe_payment,
    create_enrolment_record,
    create_or_update_hubspot_contact,
    send_confirmation_email
)

pytestmark = pytest.mark.django_db


@pytest.fixture()
def registration():
    COURSE_DURATION_IN_DAYS = 35
    first_name = 'FirstName'
    last_name = 'LastName'
    email = 'user@example.com'
    start_date = datetime.date.today()

    course = Course.objects.create(name=settings.CODING_BASICS)
    batch = Batch.objects.create(
        course=course,
        start_date=start_date,
        end_date=start_date + datetime.timedelta(COURSE_DURATION_IN_DAYS),
        capacity=18,
        sections=1
    )
    Section.objects.create(
        batch=batch,
        number=1,
        capacity=18
    )
    StudentUser.objects.create(
        email=email,
        first_name=first_name,
        last_name=last_name,
        password=settings.PLACEHOLDER_PASSWORD
    )
    registration = Registration.objects.create(
        course=course,
        batch=batch,
        first_name=first_name,
        last_name=last_name,
        email=email,
        country_of_residence='SG',
        referral_channel='word_of_mouth'
    )

    yield registration

@patch('student.models.registration.record_stripe_payment')
@patch('student.models.registration.create_enrolment_record')
@patch('student.models.registration.create_or_update_hubspot_contact')
@patch('student.models.registration.send_confirmation_email')
def test_complete_transaction(mock_record_stripe_payment,
                              mock_create_enrolment_record,
                              mock_create_or_update_hubspot_contact,
                              mock_send_confirmation_email,
                              registration):
    # This is a shortened version of event_data
    # Full details can be found in Stripe dashboard
    event_data = {
        "amount_total": 19900,
        "currency": "sgd",
        "customer": "cus_Lnh1zdmxckmUUU",
        "customer_details": {
            "email": registration.email,
        },
        "metadata": {
            "payable_id": registration.id,
            "payable_type": type(registration).__name__
        },
        "payment_intent": "pi_3L65dXHQt5htmvv4176vtmCj",
        "payment_status": "paid",
    }

    registration.complete_transaction(event_data)

    mock_record_stripe_payment.assert_called_once()
    mock_create_enrolment_record.assert_called_once()
    mock_create_or_update_hubspot_contact.assert_called_once()
    mock_send_confirmation_email.assert_called_once()

def test_record_stripe_payment(registration):
    event_data = {
        "amount_total": 19900,
        "currency": "sgd",
        "customer": "cus_Lnh1zdmxckmUUU",
        "customer_details": {
            "email": registration.email,
        },
        "metadata": {
            "payable_id": registration.id,
            "payable_type": type(registration).__name__
        },
        "payment_intent": "pi_3L65dXHQt5htmvv4176vtmCj",
        "payment_status": "paid",
    }

    record_stripe_payment(event_data)

    assert StripePayment.objects.count() == 1
    stripe_payment = StripePayment.objects.last()
    assert stripe_payment.payable_type == type(registration).__name__
    assert stripe_payment.payable_id == registration.id
    assert stripe_payment.intent == event_data['payment_intent']
    assert stripe_payment.customer == event_data['customer']
    assert stripe_payment.customer_email == event_data['customer_details']['email']
    assert stripe_payment.amount == event_data['amount_total']
    assert stripe_payment.currency == event_data['currency']
    assert stripe_payment.status == event_data['payment_status']

@patch('staff.models.batch.Batch.next_enrollable_section')
def test_create_enrolment_record(mock_next_enrollable_section, registration):
    student_user = StudentUser.objects.last()
    mock_next_enrollable_section.return_value = registration.batch.section_set.first()

    create_enrolment_record(registration.batch, student_user)

    mock_next_enrollable_section.assert_called_once()
    assert Enrolment.objects.count() == 1
    enrolment = Enrolment.objects.last()
    section = Section.objects.last()
    student_user = StudentUser.objects.get(email=registration.email)
    assert enrolment.batch == registration.batch
    assert enrolment.section == section
    assert enrolment.student_user.first_name == student_user.first_name
    assert enrolment.student_user.last_name == student_user.last_name

@patch('student.library.hubspot.Hubspot.create_contact')
def test_create_hubspot_contact_when_hubspot_contact_id_does_not_exist(mock_create_contact, registration):
    student_user = StudentUser.objects.get(email=registration.email)
    # This is a shortened version of Hubspot's response
    # Full details can be found at https://developers.hubspot.com/docs/api/crm/contacts
    mock_create_contact.return_value = {
        "id": "1",
        "properties": {
            "email": "user@example.com",
            "firstname": "FirstName",
            "lastname": "LastName",
        },
    }

    create_or_update_hubspot_contact(student_user)

    assert student_user.hubspot_contact_id == 1

@patch('student.library.hubspot.Hubspot.get_contact')
@patch('student.library.hubspot.Hubspot.update_contact')
def test_update_hubspot_contact_when_hubspot_contact_id_exists(mock_get_contact, mock_update_contact):
    learn_user_email = 'learn@email.com'
    learn_first_name = 'LearnFirstName'
    learn_last_name = 'LearnLastName'
    student_user = StudentUser.objects.create(
        email=learn_user_email,
        first_name=learn_first_name,
        last_name=learn_last_name,
        password=settings.PLACEHOLDER_PASSWORD,
        hubspot_contact_id=1
    )
    # This is a shortened version of Hubspot's response
    # Full details can be found at https://developers.hubspot.com/docs/api/crm/contacts
    mock_get_contact.return_value = {
        "properties": {
            "email": "hubspotemail@example.com",
            "firstname": "HubspotFirstName",
            "lastname": "HubspotLastName",
        },
    }

    create_or_update_hubspot_contact(student_user)

    mock_update_contact.assert_called_once()

@patch('emails.library.sendgrid.Sendgrid.send')
def test_send_confirmation_email(mock_send, registration):
    send_confirmation_email(registration.id,
                            type(registration).__name__,
                            registration.email,
                            registration.first_name,
                            registration.batch)

    mock_send.assert_called_once()
