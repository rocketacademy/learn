from django.db import models
from django.utils.crypto import get_random_string
from safedelete import SOFT_DELETE
from safedelete.models import SafeDeleteModel

PERCENTAGE = 'percent'
DOLLARS = 'dollars'


class Coupon(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE

    REFERRAL = 'referral'
    PARTNERSHIP = 'partnership'
    TYPE_CHOICES = [
        (REFERRAL, 'Referral'),
        (PARTNERSHIP, 'Partnership')
    ]

    DISCOUNT_TYPE_CHOICES = [
        (PERCENTAGE, 'Percent off'),
        (DOLLARS, 'Dollars off'),
    ]

    code = models.CharField(max_length=6, blank=True)
    couponable_type = models.CharField(max_length=50, null=True, blank=True)
    couponable_id = models.PositiveIntegerField(null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    discount_type = models.CharField(max_length=7, choices=DISCOUNT_TYPE_CHOICES)
    discount_amount = models.PositiveIntegerField()
    description = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.code = get_random_string(length=6)

        if self.end_date and self.start_date >= self.end_date:
            raise ValueError('Coupon end date should be after start date')

        return super().save(*args, **kwargs)

    def get_discount_display(self):
        if self.discount_type == PERCENTAGE:
            return f"{self.discount_amount}%"
        elif self.discount_type == DOLLARS:
            return f"${self.discount_amount}"
