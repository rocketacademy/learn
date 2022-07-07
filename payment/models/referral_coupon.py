from django.db import models
from payment.models.coupon import Coupon


class ReferralCoupon(Coupon):
    referrer_email = models.EmailField(max_length=254, unique=True)
