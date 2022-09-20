from django.db import models
from django.contrib.auth import get_user_model

from payment.models import Coupon

User = get_user_model()


class ReferralCoupon(Coupon):
    referrer = models.ForeignKey(User, on_delete=models.CASCADE)
