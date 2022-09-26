from django.db import models

from emails.models import SendgridEvent


class GroupResubscribeSendgridEvent(SendgridEvent):
    event = models.CharField(max_length=16, default=SendgridEvent.GROUP_RESUBSCRIBE, editable=False)
    useragent = models.CharField(max_length=200)
    ip = models.CharField(max_length=50)
    url = models.URLField()
    asm_group_id = models.IntegerField()
