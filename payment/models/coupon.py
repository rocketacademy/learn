from django.db import models
from django.utils.crypto import get_random_string
from django.utils.html import format_html
from polymorphic.models import PolymorphicModel
from safedelete import SOFT_DELETE
from safedelete.models import SafeDeleteModel

from payment.models.coupon_effect import CouponEffect


class Coupon(PolymorphicModel, SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE

    code = models.CharField(max_length=15, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    effects = models.ManyToManyField(CouponEffect)
    description = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # only validate if object is new
        # because we should not validate the coupon's code when users update other attributes
        if not self.pk:
            # generate a random code if user did not provide one
            if not self.code:
                random_code = get_random_string(length=6)

                # ensure that generated code is not already being used by existing coupons
                while Coupon.objects.filter(code=random_code).exists():
                    random_code = get_random_string(length=6)

                self.code = random_code
            # disallow users from creating coupons with codes that already exist
            if self.code and Coupon.objects.filter(code=self.code).exists():
                raise ValueError(f"Coupon with code {self.code} already exists")

        if self.end_date and self.start_date >= self.end_date:
            raise ValueError('Coupon end date should be after start date')

        return super().save(*args, **kwargs)

    def get_effects_display(self):
        couponeffect_queryset = self.effects.all()
        html_formatted_effects_display = ""

        for coupon_effect in couponeffect_queryset:
            html_formatted_effects_display += f"{coupon_effect}<br>"

        return format_html(html_formatted_effects_display)

    def biggest_discount_for(self, course, original_price):
        coupon_effects = self.effects.filter(
            couponable_type=type(course).__name__,
            couponable_id=course.id
        )
        biggest_discount = 0

        for coupon_effect in coupon_effects:
            if coupon_effect.discount_type == CouponEffect.PERCENTAGE:
                amount = original_price * coupon_effect.discount_amount / 100

                if amount > biggest_discount:
                    biggest_discount = amount
            elif coupon_effect.discount_type == CouponEffect.DOLLARS:
                if coupon_effect.discount_amount > biggest_discount:
                    biggest_discount = coupon_effect.discount_amount

        return biggest_discount
