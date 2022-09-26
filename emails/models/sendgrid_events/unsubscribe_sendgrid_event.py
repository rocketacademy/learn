from django.db import models

from emails.models import SendgridEvent


class UnsubsribeSendgridEvent(SendgridEvent):
    event = models.CharField(max_length=11, default=SendgridEvent.UNSUBSCRIBE, editable=False)
