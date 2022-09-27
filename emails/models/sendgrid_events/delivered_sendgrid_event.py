from django.db import models

from emails.models import SendgridEvent


class DeliveredSendgridEvent(SendgridEvent):
    event = models.CharField(max_length=9, default=SendgridEvent.DELIVERED, editable=False)
    smtp_id = models.CharField(max_length=35)
    ip = models.CharField(max_length=50)
