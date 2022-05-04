from django.db import models
from polymorphic.models import PolymorphicModel
from safedelete import SOFT_DELETE_CASCADE
from safedelete.models import SafeDeleteModel
from registration import Registration


PENDING = 'PENDING'
PAID = 'PAID'
UNSUCCESSFUL = 'UNSUCCESSFUL'

STATUS_CHOICES = [
    (PENDING, 'pending'),
    (PAID, 'paid'),
    (UNSUCCESSFUL, 'unsuccessful'),
]


class Payment(PolymorphicModel):
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
