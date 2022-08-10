from django.db import models
from payment.models.discount import Discount


class StripeDiscount(Discount):
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    coupon_id = models.CharField(max_length=8)
