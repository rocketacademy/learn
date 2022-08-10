import datetime
from django.conf import settings
import pytest

from authentication.models import StudentUser
from emails.library.sendgrid import Sendgrid
from payment.models.stripe_discount import StripeDiscount
from payment.models.stripe_payment import StripePayment
from staff.models.batch import Batch
from staff.models.course import Course
from staff.models.section import Section
from student.library.hubspot import Hubspot
from student.models.enrolment import Enrolment
from student.models.registration import Registration

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

def test_complete_transaction(mocker, registration):
    mocker.patch('student.models.registration.Registration.record_stripe_payment')
    mocker.patch('student.models.registration.Registration.create_enrolment_record')
    mocker.patch('student.models.registration.Registration.create_or_update_hubspot_contact')
    mocker.patch('student.models.registration.Registration.send_confirmation_email')
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

    registration.record_stripe_payment.assert_called_once()
    registration.create_enrolment_record.assert_called_once()
    registration.create_or_update_hubspot_contact.assert_called_once()
    registration.send_confirmation_email.assert_called_once()

def test_record_stripe_payment(registration):
    original_amount = 19900
    discount_amount = 1500
    amount_after_discount = original_amount - discount_amount
    event_data = {
        "amount_total": amount_after_discount,
        "amount_subtotal": original_amount,
        "currency": "sgd",
        "customer": "cus_Lnh1zdmxckmUUU",
        "customer_details": {
            "email": registration.email,
        },
        "metadata": {
            "payable_id": registration.id,
            "payable_type": type(registration).__name__,
            "stripe_coupon_id": '4OM9lIyP'
        },
        "payment_intent": "pi_3L65dXHQt5htmvv4176vtmCj",
        "payment_status": "paid",
        "total_details": {
            "amount_discount": discount_amount,
        },
    }

    registration.record_stripe_payment(event_data)

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
    assert stripe_payment.discount.original_amount == event_data['amount_subtotal']
    assert stripe_payment.discount.amount == event_data['total_details']['amount_discount']
    assert stripe_payment.discount.coupon_id == event_data['metadata']['stripe_coupon_id']

def test_create_enrolment_record(mocker, registration):
    student_user = StudentUser.objects.last()
    mocker.patch(
        'staff.models.batch.Batch.next_enrollable_section',
        return_value=registration.batch.section_set.first()
    )

    registration.create_enrolment_record(student_user)

    Batch.next_enrollable_section.assert_called_once()
    assert Enrolment.objects.count() == 1
    enrolment = Enrolment.objects.last()
    section = Section.objects.last()
    student_user = StudentUser.objects.get(email=registration.email)
    assert enrolment.registration == registration
    assert enrolment.batch == registration.batch
    assert enrolment.section == section
    assert enrolment.student_user.first_name == student_user.first_name
    assert enrolment.student_user.last_name == student_user.last_name

def test_update_hubspot_contact_when_hubspot_contact_id_exists_in_learn(mocker, registration):
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
    mocker.patch(
        'student.library.hubspot.Hubspot.get_contact_by_id',
        return_value={
            'properties': {
                'email': 'hubspotemail@example.com',
                'firstname': 'HubspotFirstName',
                'lastname': 'HubspotLastName',
            },
        }
    )

    mocker.patch(
        'student.library.hubspot.Hubspot.update_contact',
        return_value={
            "properties": {
                "email": "hubspotemail@example.com",
                "firstname": "HubspotFirstName",
                "lastname": "HubspotLastName",
            },
        }
    )

    registration.create_or_update_hubspot_contact(student_user)

    Hubspot.update_contact.assert_called_once()

def test_create_hubspot_contact_when_hubspot_contact_does_not_exist(mocker, registration):
    student_user = StudentUser.objects.get(email=registration.email)
    mocker.patch(
        'student.library.hubspot.Hubspot.get_contact_by_email',
        return_value={
            "total": "0",
            "results": [],
        }
    )
    # This is a shortened version of Hubspot's response
    # Full details can be found at https://developers.hubspot.com/docs/api/crm/contacts
    mocker.patch(
        'student.library.hubspot.Hubspot.create_contact',
        return_value={
            'id': '1',
            'properties': {
                'email': 'user@example.com',
                'firstname': 'FirstName',
                'lastname': 'LastName',
            },
        }
    )

    registration.create_or_update_hubspot_contact(student_user)

    assert student_user.hubspot_contact_id == 1

def test_update_hubspot_contact_when_contact_created_separately_in_hubspot(mocker, registration):
    student_user = StudentUser.objects.get(email=registration.email)
    mocker.patch(
        'student.library.hubspot.Hubspot.get_contact_by_email',
        return_value={
            'total': 1,
            'results': [
                {
                    'id': '651',
                    'properties':
                        {
                            'email': 'user@example.com',
                            'firstname': 'Another',
                            'hs_object_id': '651',
                            'lastname': 'Name'
                        },
                        'archived': False
                }
            ]
        }
    )
    mocker.patch('student.library.hubspot.Hubspot.update_contact')

    registration.create_or_update_hubspot_contact(student_user)

    Hubspot.update_contact.assert_called_once()

def test_send_confirmation_email(mocker, registration):
    mocker.patch('emails.library.sendgrid.Sendgrid.send')

    registration.send_confirmation_email()

    Sendgrid.send.assert_called_once()
