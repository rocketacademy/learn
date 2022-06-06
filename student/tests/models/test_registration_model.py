import datetime
from django.conf import settings
from django.contrib.auth import get_user_model
import pytest
from emails.models import SendgridEmail

from payment.models import StripePayment
from staff.models.batch import Batch
from staff.models.course import Course
from staff.models.section import Section
from student.models.enrolment import Enrolment
from student.models.registration import Registration

pytestmark = pytest.mark.django_db
User = get_user_model()
user_email = 'user@email.com'

@pytest.fixture()
def registration():
    COURSE_DURATION_IN_DAYS = 35
    first_name = 'FirstName'
    last_name = 'LastName'
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
    User.objects.create(
        email=user_email,
        first_name=first_name,
        last_name=last_name,
        password=settings.PLACEHOLDER_PASSWORD
    )
    registration = Registration.objects.create(
        course=course,
        batch=batch,
        first_name=first_name,
        last_name=last_name,
        email=user_email,
        country_of_residence='SG',
        referral_channel='word_of_mouth'
    )

    yield registration


def test_complete_transaction(registration):
    # This is a shortened version of event_data
    # Full details can be found in Stripe dashboard
    event_data = {
        "amount_total": 19900,
        "currency": "sgd",
        "customer": "cus_Lnh1zdmxckmUUU",
        "customer_details": {
            "email": user_email,
        },
        "metadata": {
            "payable_id": registration.id,
            "payable_type": type(registration).__name__
        },
        "payment_intent": "pi_3L65dXHQt5htmvv4176vtmCj",
        "payment_status": "paid",
    }

    registration.complete_transaction(event_data)

    assert Enrolment.objects.count() == 1
    enrolment = Enrolment.objects.last()
    section = Section.objects.last()
    user = User.objects.get(email=user_email)
    assert enrolment.batch == registration.batch
    assert enrolment.section == section
    assert enrolment.user == user

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

    assert SendgridEmail.objects.count() == 1
    sendgrid_email = SendgridEmail.objects.last()
    assert sendgrid_email.template_id == settings.CODING_BASICS_REGISTRATION_CONFIRMATION_TEMPLATE_ID
    assert sendgrid_email.emailable_id == registration.id
    assert sendgrid_email.emailable_type == type(registration).__name__
    assert sendgrid_email.recipient_email == registration.email
    assert sendgrid_email.sender_email == settings.ROCKET_EMAIL
