from django.conf import settings
from django.http import HttpResponseServerError
from sendgrid import SendGridAPIClient

from emails.models import SendgridEmail


class Sendgrid:
    def __init__(self):
        self.client = SendGridAPIClient(settings.SENDGRID_API_KEY)

    def send(self, message):
        try:
            self.client.send(message)
            SendgridEmail.objects.create(
                emailable_id=self.id,
                emailable_type=type(self).__name__,
                sender_email=message.from_email,
                recipient_email=message.to_email,
                template_id=message.template_id,
            )
        except Exception as error:
            return HttpResponseServerError(f'Could not send registration confirmation email: {str(error)}')
