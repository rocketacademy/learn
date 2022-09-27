from django.db import models

from emails.models import SendgridEvent


class ProcessedSendgridEvent(SendgridEvent):
    event = models.CharField(max_length=9, default=SendgridEvent.PROCESSED, editable=False)
    smtp_id = models.CharField(max_length=35)
