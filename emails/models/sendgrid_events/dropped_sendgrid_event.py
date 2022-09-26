from django.db import models

from emails.models import SendgridEvent


class DroppedSendgridEvent(SendgridEvent):
    event = models.CharField(max_length=7, default=SendgridEvent.DROPPED, editable=False)
    reason = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
