from django.db import models

from emails.models import SendgridEvent


class DeferredSendgridEvent(SendgridEvent):
    event = models.CharField(max_length=8, default=SendgridEvent.DEFERRED, editable=False)
    attempt = models.PositiveIntegerField()
