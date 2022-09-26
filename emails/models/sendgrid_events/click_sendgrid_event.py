from django.db import models

from emails.models import SendgridEvent


class ClickSendgridEvent(SendgridEvent):
    event = models.CharField(max_length=5, default=SendgridEvent.CLICK, editable=False)
    useragent = models.CharField(max_length=200)
    ip = models.CharField(max_length=50)
    url = models.URLField()
