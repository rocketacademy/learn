from django.db import models

from payment.models.coupon_effect import CouponEffect


class StripeCouponEffect(CouponEffect):
    stripe_coupon_id = models.CharField(max_length=8, null=True)
