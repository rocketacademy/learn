from django.db import models
from polymorphic.models import PolymorphicModel
from safedelete import SOFT_DELETE_CASCADE
from safedelete.models import SafeDeleteModel


class SendgridEmailTemplate(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    name = models.CharField(max_length=100)
    template_id = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Email(PolymorphicModel, SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    emailable_id = models.IntegerField()
    emailable_type = models.CharField(max_length=50)
    recipient_email = models.CharField(max_length=255)
    sender_email = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class SendgridEmail(Email):
    sendgrid_email_template = models.ForeignKey(SendgridEmailTemplate, on_delete=models.CASCADE)
