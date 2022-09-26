from django.db import models

from emails.models import SendgridEvent


class SpamReportSendgridEvent(SendgridEvent):
    event = models.CharField(max_length=10, default=SendgridEvent.SPAM_REPORT, editable=False)
