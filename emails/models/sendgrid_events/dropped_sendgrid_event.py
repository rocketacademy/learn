from django.db import models

from emails.models import SendgridEvent


class DroppedSendgridEvent(SendgridEvent):
    event = models.CharField(max_length=7, default=SendgridEvent.DROPPED, editable=False)
    smtp_id = models.CharField(max_length=35)
    reason = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
