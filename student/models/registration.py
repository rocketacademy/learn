from django.conf import settings
from django.db import models
import pytz
from safedelete import SOFT_DELETE_CASCADE
from safedelete.models import SafeDeleteModel
from sendgrid.helpers.mail import Mail

from authentication.models import StudentUser
from emails.models import SendgridEmail
from emails.library.sendgrid import Sendgrid
from payment.models import StripePayment
from staff.models.batch import Batch
from staff.models.course import Course
from student.library.hubspot import Hubspot, contact_requires_update
from student.models.enrolment import Enrolment


class Registration(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    WORD_OF_MOUTH = 'word_of_mouth'
    LINKEDIN = 'linkedin'
    GOOGLE = 'google'
    FACEBOOK = 'facebook'
    YOUTUBE = 'youtube'
    INSTAGRAM = 'instagram'

    REFERRAL_CHANNELS = [
        (WORD_OF_MOUTH, 'Word of mouth'),
        (LINKEDIN, 'LinkedIn'),
        (GOOGLE, 'Google'),
        (FACEBOOK, 'Facebook'),
        (YOUTUBE, 'YouTube'),
        (INSTAGRAM, 'Instagram'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    country_of_residence = models.CharField(max_length=255, choices=pytz.country_names.items())
    referral_channel = models.CharField(max_length=255, choices=REFERRAL_CHANNELS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def complete_transaction(self, event_data):
        student_user = StudentUser.objects.get(email=self.email)

        record_stripe_payment(event_data)
        create_enrolment_record(self.batch, student_user)
        create_or_update_hubspot_contact(student_user)
        send_confirmation_email(self.email, self.first_name, self.batch)

def record_stripe_payment(event_data):
    StripePayment.objects.create(
        payable_type=event_data['metadata']['payable_type'],
        payable_id=event_data['metadata']['payable_id'],
        intent=event_data['payment_intent'],
        customer=event_data['customer'],
        customer_email=event_data['customer_details']['email'],
        amount=event_data['amount_total'],
        currency=event_data['currency'],
        status=event_data['payment_status']
    )

def create_enrolment_record(batch, student_user):
    next_enrollable_section = batch.next_enrollable_section()

    Enrolment.objects.create(
        batch=batch,
        section=next_enrollable_section,
        user=student_user
    )

def create_or_update_hubspot_contact(student_user):
    hubspot_client = Hubspot()
    properties = {
        'email': student_user.email,
        'firstname': student_user.first_name,
        'lastname': student_user.last_name
    }

    if student_user.hubspot_contact_id:
        hubspot_contact = hubspot_client.get_contact(student_user.hubspot_contact_id)['properties']

        if contact_requires_update(student_user, hubspot_contact) is True:
            hubspot_client.update_contact(student_user.hubspot_contact_id, properties)
    else:
        hubspot_contact = hubspot_client.create_contact(properties)
        student_user.hubspot_contact_id = int(hubspot_contact['id'])
        student_user.save()

def send_confirmation_email(email, first_name, batch):
    from_email = settings.ROCKET_EMAIL
    to_email = email
    template_id = settings.CODING_BASICS_REGISTRATION_CONFIRMATION_TEMPLATE_ID

    message = Mail(
        from_email=from_email,
        to_emails=to_email,
    )
    message.dynamic_template_data = {
        'first_name': first_name.capitalize(),
        'email': to_email,
        'start_date': batch.start_date.strftime('%A, %d %b %Y')
    }
    message.template_id = template_id

    sendgrid_client = Sendgrid()
    sendgrid_client.send(message)
