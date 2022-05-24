from django.db import models
from safedelete import SOFT_DELETE_CASCADE
from safedelete.models import SafeDeleteModel
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


class Correspondence(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    content = models.TextField()
    receiver = models.CharField(max_length=255)
    sent_at = models.DateTimeField(auto_now_add=True)

    def send_registration_confirmation_email(self, student_email):
        message = Mail(
            from_email='hello@rocketacademy.co',
            to_emails=student_email,
            subject='Your registration has been confirmed',
            html_content='<strong>Thank you for registering for Codind Basics!</strong>')
        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e.message)
