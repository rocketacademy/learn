from django.conf import settings
from django.http import HttpResponseServerError
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from emails.models import SendgridEmail


class Sendgrid:
    def __init__(self):
        self.client = SendGridAPIClient(settings.SENDGRID_API_KEY)

    def send(self,
             emailable_id,
             emailable_class_name,
             from_email,
             to_email,
             template_id,
             message):
        try:
            self.client.send(message)
            SendgridEmail.objects.create(
                emailable_id=emailable_id,
                emailable_type=emailable_class_name,
                sender_email=from_email,
                recipient_email=to_email,
                template_id=template_id,
            )
        except Exception as error:
            return HttpResponseServerError(f'Could not send email for {emailable_class_name} - {emailable_id}: {str(error)}')

    def send_bulk(self,
                  from_email,
                  to_emails,
                  template_id):
        message = Mail(
            from_email=(from_email, settings.ORGANISATION_NAME),
            to_emails=to_emails,
            is_multiple=True)
        message.template_id = template_id

        try:
            self.client.send(message)
        except Exception as error:
            return HttpResponseServerError(f'Error sending bulk email: {str(error)}')
