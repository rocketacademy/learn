from django.apps import apps
from django.db import models
from safedelete import SOFT_DELETE
from safedelete.models import SafeDeleteModel


class CouponEffect(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE

    PERCENTAGE = 'percent'
    DOLLARS = 'dollars'

    DISCOUNT_TYPE_CHOICES = [
        (PERCENTAGE, 'Percent off'),
        (DOLLARS, 'Dollars off'),
    ]
    couponable_type = models.CharField(max_length=50, null=True, blank=True)
    couponable_id = models.PositiveIntegerField(null=True, blank=True)
    discount_type = models.CharField(max_length=7, choices=DISCOUNT_TYPE_CHOICES)
    discount_amount = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.discount_type == self.PERCENTAGE:
            string_representation = f"{self.discount_amount}% off"
        elif self.discount_type == self.DOLLARS:
            string_representation = f"${self.discount_amount} off"

        if self.couponable_type and self.couponable_id:
            couponable_object = apps.get_model('staff', self.couponable_type).objects.get(pk=self.couponable_id)

            string_representation = string_representation + f" {couponable_object.get_name_display()}"

        return string_representation
