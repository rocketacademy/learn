from django.db import models
from polymorphic.models import PolymorphicModel


class Payment(PolymorphicModel):
    payable_id = models.IntegerField()
    payable_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class StripePayment(Payment):
    intent = models.CharField(max_length=50)
    customer = models.CharField(max_length=50)
    customer_email = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=5)
    status = models.CharField(max_length=20)
