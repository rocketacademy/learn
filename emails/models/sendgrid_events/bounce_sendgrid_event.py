from django.db import models

from emails.models import SendgridEvent


class BounceSendgridEvent(SendgridEvent):
    event = models.CharField(max_length=6, default=SendgridEvent.BOUNCE, editable=False)
    bounce_classification = models.CharField(max_length=20)
    smtp_id = models.CharField(max_length=35)
    ip = models.CharField(max_length=50)
    reason = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
