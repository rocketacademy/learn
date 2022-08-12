from django.db import models
from payment.models.payment import Payment
from payment.models.stripe_discount import StripeDiscount


class StripePayment(Payment):
    intent = models.CharField(max_length=50)
    customer = models.CharField(max_length=50)
    customer_email = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=5)
    status = models.CharField(max_length=20)
    discount = models.OneToOneField(StripeDiscount, on_delete=models.CASCADE, null=True, blank=True)
