from django.conf import settings
import pytest

from emails.library.sendgrid import Sendgrid
from payment.models.stripe_payment import StripePayment
from staff.models.batch import Batch
from staff.models.section import Section
from student.library.hubspot import Hubspot
from student.models.enrolment import Enrolment

pytestmark = pytest.mark.django_db


def test_complete_transaction(mocker, student_user_factory, swe_fundamentals_registration):
    student_user = student_user_factory()
    swe_fundamentals_registration.first_name = student_user.first_name
    swe_fundamentals_registration.last_name = student_user.last_name
    swe_fundamentals_registration.email = student_user.email
    swe_fundamentals_registration.save()
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
            "email": swe_fundamentals_registration.email,
        },
        "metadata": {
            "payable_id": swe_fundamentals_registration.id,
            "payable_type": type(swe_fundamentals_registration).__name__
        },
        "payment_intent": "pi_3L65dXHQt5htmvv4176vtmCj",
        "payment_status": "paid",
    }

    swe_fundamentals_registration.complete_transaction(event_data)

    swe_fundamentals_registration.record_stripe_payment.assert_called_once()
    swe_fundamentals_registration.create_enrolment_record.assert_called_once()
    swe_fundamentals_registration.create_or_update_hubspot_contact.assert_called_once()
    swe_fundamentals_registration.send_confirmation_email.assert_called_once()

def test_record_stripe_payment(swe_fundamentals_registration):
    original_amount = 19900
    discount_amount = 1500
    amount_after_discount = original_amount - discount_amount
    event_data = {
        "amount_total": amount_after_discount,
        "amount_subtotal": original_amount,
        "currency": "sgd",
        "customer": "cus_Lnh1zdmxckmUUU",
        "customer_details": {
            "email": swe_fundamentals_registration.email,
        },
        "metadata": {
            "payable_id": swe_fundamentals_registration.id,
            "payable_type": type(swe_fundamentals_registration).__name__,
            "stripe_coupon_id": '4OM9lIyP'
        },
        "payment_intent": "pi_3L65dXHQt5htmvv4176vtmCj",
        "payment_status": "paid",
        "total_details": {
            "amount_discount": discount_amount,
        },
    }

    swe_fundamentals_registration.record_stripe_payment(event_data)

    assert StripePayment.objects.count() == 1
    stripe_payment = StripePayment.objects.last()
    assert stripe_payment.payable_type == type(swe_fundamentals_registration).__name__
    assert stripe_payment.payable_id == swe_fundamentals_registration.id
    assert stripe_payment.intent == event_data['payment_intent']
    assert stripe_payment.customer == event_data['customer']
    assert stripe_payment.customer_email == event_data['customer_details']['email']
    assert stripe_payment.amount == event_data['amount_total']
    assert stripe_payment.currency == event_data['currency']
    assert stripe_payment.status == event_data['payment_status']
    assert stripe_payment.discount.amount == event_data['total_details']['amount_discount']
    assert stripe_payment.discount.coupon_id == event_data['metadata']['stripe_coupon_id']

def test_create_enrolment_record(mocker, student_user_factory, swe_fundamentals_registration):
    student_user = student_user_factory()
    swe_fundamentals_registration.first_name = student_user.first_name
    swe_fundamentals_registration.last_name = student_user.last_name
    swe_fundamentals_registration.email = student_user.email
    swe_fundamentals_registration.save()
    mocker.patch(
        'staff.models.batch.Batch.next_enrollable_section',
        return_value=swe_fundamentals_registration.batch.section_set.first()
    )

    swe_fundamentals_registration.create_enrolment_record(student_user)

    Batch.next_enrollable_section.assert_called_once()
    assert Enrolment.objects.count() == 1
    enrolment = Enrolment.objects.last()
    section = Section.objects.last()
    assert enrolment.registration == swe_fundamentals_registration
    assert enrolment.batch == swe_fundamentals_registration.batch
    assert enrolment.section == section
    assert enrolment.student_user.first_name == student_user.first_name
    assert enrolment.student_user.last_name == student_user.last_name

def test_update_hubspot_contact_when_hubspot_contact_id_exists_in_learn(mocker, student_user_factory, swe_fundamentals_registration):
    hubspot_contact_id = 1234
    student_user = student_user_factory.create(hubspot_contact_id=hubspot_contact_id)
    swe_fundamentals_registration.first_name = student_user.first_name
    swe_fundamentals_registration.last_name = student_user.last_name
    swe_fundamentals_registration.email = student_user.email
    swe_fundamentals_registration.save()
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

    swe_fundamentals_registration.create_or_update_hubspot_contact(student_user)

    Hubspot.update_contact.assert_called_once_with(
        hubspot_contact_id,
        {
            'email': student_user.email,
            'firstname': student_user.first_name,
            'lastname': student_user.last_name,
            'funnel_status': settings.BASICS_ENROLLED_FUNNEL_STATUS,
            'basics_batch_number': swe_fundamentals_registration.batch.number,
            'contact_source': settings.PROJECT_NAME,
            'referral_code': swe_fundamentals_registration.referral_code
        }
    )

def test_create_hubspot_contact_when_hubspot_contact_does_not_exist(mocker, student_user_factory, swe_fundamentals_registration):
    student_user = student_user_factory()
    swe_fundamentals_registration.first_name = student_user.first_name
    swe_fundamentals_registration.last_name = student_user.last_name
    swe_fundamentals_registration.email = student_user.email
    swe_fundamentals_registration.save()
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

    swe_fundamentals_registration.create_or_update_hubspot_contact(student_user)

    assert student_user.hubspot_contact_id == 1

def test_update_hubspot_contact_when_contact_created_separately_in_hubspot(mocker, student_user_factory, swe_fundamentals_registration):
    student_user = student_user_factory()
    swe_fundamentals_registration.first_name = student_user.first_name
    swe_fundamentals_registration.last_name = student_user.last_name
    swe_fundamentals_registration.email = student_user.email
    swe_fundamentals_registration.save()
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
                            'hs_object_id': 651,
                            'lastname': 'Name'
                        },
                        'archived': False
                }
            ]
        }
    )
    mocker.patch('student.library.hubspot.Hubspot.update_contact')

    swe_fundamentals_registration.create_or_update_hubspot_contact(student_user)

    Hubspot.update_contact.assert_called_once_with(
        student_user.hubspot_contact_id,
        {
            'email': student_user.email,
            'firstname': student_user.first_name,
            'lastname': student_user.last_name,
            'funnel_status': settings.BASICS_ENROLLED_FUNNEL_STATUS,
            'basics_batch_number': swe_fundamentals_registration.batch.number,
            'contact_source': settings.PROJECT_NAME,
            'referral_code': swe_fundamentals_registration.referral_code
        }
    )

def test_send_confirmation_email(mocker, swe_fundamentals_registration):
    mocker.patch('emails.library.sendgrid.Sendgrid.send')

    swe_fundamentals_registration.send_confirmation_email()

    Sendgrid.send.assert_called_once()

def test_payment_returns_payment_object_if_exists(swe_fundamentals_registration):
    payment = StripePayment.objects.create(
        payable_type=type(swe_fundamentals_registration).__name__,
        payable_id=swe_fundamentals_registration.id,
        intent='pi_3L65dXHQt5htmvv4176vtmCj',
        customer='cus_Lnh1zdmxckmUUU',
        customer_email='customer_email@example.com',
        amount=settings.SWE_FUNDAMENTALS_REGISTRATION_FEE_SGD * settings.CENTS_PER_DOLLAR,
        currency=settings.SINGAPORE_DOLLAR_CURRENCY,
        status='paid'
    )

    associated_payment = swe_fundamentals_registration.payment()

    assert associated_payment == payment

def test_payment_returns_none_if_does_not_exist(swe_fundamentals_registration):
    associated_payment = swe_fundamentals_registration.payment()

    assert associated_payment is None
