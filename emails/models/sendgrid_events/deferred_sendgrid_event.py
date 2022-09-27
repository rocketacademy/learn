from django.db import models

from emails.models import SendgridEvent


class DeferredSendgridEvent(SendgridEvent):
    event = models.CharField(max_length=8, default=SendgridEvent.DEFERRED, editable=False)
    smtp_id = models.CharField(max_length=35)
    ip = models.CharField(max_length=50)
    attempt = models.IntegerField()
