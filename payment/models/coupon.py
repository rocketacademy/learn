from django.db import models
from django.utils.crypto import get_random_string
from django.utils.html import format_html
from safedelete import SOFT_DELETE
from safedelete.models import SafeDeleteModel

from payment.models.coupon_effect import CouponEffect


class Coupon(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE

    code = models.CharField(max_length=6, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    effects = models.ManyToManyField(CouponEffect)
    description = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.code = get_random_string(length=6)

        if self.end_date and self.start_date >= self.end_date:
            raise ValueError('Coupon end date should be after start date')

        return super().save(*args, **kwargs)

    def get_effects_display(self):
        couponeffect_queryset = self.effects.all()
        html_formatted_effects_display = ""

        for coupon_effect in couponeffect_queryset:
            html_formatted_effects_display += f"{coupon_effect}<br>"

        return format_html(html_formatted_effects_display)
