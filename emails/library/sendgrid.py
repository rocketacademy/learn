from django.conf import settings
from django.http import HttpResponseServerError
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import CustomArg, Mail


class Sendgrid:
    def __init__(self):
        self.client = SendGridAPIClient(settings.SENDGRID_API_KEY)

    def send(self,
             emailable_id,
             emailable_class_name,
             from_email,
             to_email,
             dynamic_template_data,
             template_id):
        try:
            message = Mail(
                from_email=(from_email, settings.ROCKET_ACADEMY),
                to_emails=to_email,
            )
            message.dynamic_template_data = dynamic_template_data
            message.template_id = template_id
            message.custom_arg = CustomArg('emailable_id', emailable_id)
            message.custom_arg = CustomArg('emailable_type', emailable_class_name)

            response = self.client.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as error:
            return HttpResponseServerError(f'Error sending email for {emailable_class_name} - {emailable_id}: {str(error)}')

    def send_bulk(self, from_email, personalizations, template_id):
        message = Mail(from_email=(from_email, settings.ROCKET_ACADEMY))
        message.template_id = template_id

        for personalization in personalizations:
            message.add_personalization(personalization)

        try:
            self.client.send(message)
        except Exception as error:
            return HttpResponseServerError(f'Error sending bulk email: {str(error)}')
