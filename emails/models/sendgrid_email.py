from django.db import models

from emails.models import Email


class SendgridEmail(Email):
    template_id = models.CharField(max_length=50)
