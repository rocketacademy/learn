from django.db import models
from safedelete import SOFT_DELETE
from safedelete.models import SafeDeleteModel


class SendgridEvent(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE

    PROCESSED = 'processed'
    DROPPED = 'dropped'
    DELIVERED = 'delivered'
    DEFERRED = 'deferred'
    BOUNCE = 'bounce'

    emailable_id = models.PositiveIntegerField()
    emailable_type = models.CharField(max_length=50)
    recipient_email = models.CharField(max_length=255)
    timestamp = models.PositiveIntegerField()
    sg_event_id = models.CharField(max_length=100)
    sg_message_id = models.CharField(max_length=100)
    sg_template_id = models.CharField(max_length=34, null=True)
    sg_template_name = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
