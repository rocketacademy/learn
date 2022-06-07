from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.http import HttpResponseServerError
import pytz
from python_http_client.exceptions import HTTPError
from safedelete import SOFT_DELETE_CASCADE
from safedelete.models import SafeDeleteModel
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from emails.models import SendgridEmail
from payment.models import StripePayment
from staff.models.batch import Batch
from staff.models.course import Course
from student.models.enrolment import Enrolment

User = get_user_model()


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
        next_enrollable_section = self.batch.next_enrollable_section()
        user = User.objects.get(email=self.email)

        self.record_stripe_payment(event_data)
        Enrolment.objects.create(
            batch=self.batch,
            section=next_enrollable_section,
            user=user
        )
        self.send_confirmation_email()

    def record_stripe_payment(self, event_data):
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

    def send_confirmation_email(self):
        from_email = settings.ROCKET_EMAIL
        to_email = self.email
        template_id = settings.CODING_BASICS_REGISTRATION_CONFIRMATION_TEMPLATE_ID

        message = Mail(
            from_email=from_email,
            to_emails=to_email,
        )
        message.dynamic_template_data = {
            'first_name': self.first_name.capitalize(),
            'email': to_email,
            'start_date': self.batch.start_date.strftime('%A, %d %b %Y')
        }
        message.template_id = template_id

        try:
            sendgrid_client = SendGridAPIClient(settings.SENDGRID_API_KEY)
            sendgrid_client.send(message)
            SendgridEmail.objects.create(
                emailable_id=self.id,
                emailable_type=type(self).__name__,
                sender_email=from_email,
                recipient_email=to_email,
                template_id=template_id,
            )
        except Exception as error:
            return HttpResponseServerError(f'Could not send registration confirmation email: {str(error)}')
