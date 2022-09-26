from django.db import models

from emails.models import SendgridEvent


class OpenSendgridEvent(SendgridEvent):
    event = models.CharField(max_length=4, default=SendgridEvent.OPEN, editable=False)
    sg_machine_open = models.CharField(max_length=5)
    useragent = models.CharField(max_length=200)
    ip = models.CharField(max_length=50)
