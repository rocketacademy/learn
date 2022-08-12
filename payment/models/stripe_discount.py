from django.db import models
from payment.models.discount import Discount


class StripeDiscount(Discount):
    coupon_id = models.CharField(max_length=8)
