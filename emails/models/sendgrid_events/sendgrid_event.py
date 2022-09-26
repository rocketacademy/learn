from django.db import models
from polymorphic.models import PolymorphicModel
from safedelete import SOFT_DELETE
from safedelete.models import SafeDeleteModel


class SendgridEvent(PolymorphicModel, SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE

    PROCESSED = 'processed'
    DEFERRED = 'deferred'
    DELIVERED = 'delivered'
    OPEN = 'open'
    CLICK = 'click'
    BOUNCE = 'bounce'
    DROPPED = 'dropped'
    SPAM_REPORT = 'spamreport'
    UNSUBSCRIBE = 'unsubscribe'
    GROUP_UNSUBSCRIBE = 'group_unsubscribe'
    GROUP_RESUBSCRIBE = 'group_resubscribe'

    emailable_id = models.IntegerField()
    emailable_type = models.CharField(max_length=50)
    recipient_email = models.CharField(max_length=255)
    timestamp = models.CharField(max_length=20)
    smtp_id = models.CharField(max_length=35)
    sg_event_id = models.CharField(max_length=100)
    sg_message_id = models.CharField(max_length=100)
    category = models.CharField(max_length=200)
