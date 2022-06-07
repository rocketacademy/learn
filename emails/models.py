from django.db import models
from polymorphic.models import PolymorphicModel
from safedelete import SOFT_DELETE_CASCADE
from safedelete.models import SafeDeleteModel


class Email(PolymorphicModel, SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    emailable_id = models.IntegerField()
    emailable_type = models.CharField(max_length=50)
    recipient_email = models.CharField(max_length=255)
    sender_email = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class SendgridEmail(Email):
    template_id = models.CharField(max_length=50)
