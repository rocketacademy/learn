from django.db import models
from polymorphic.models import PolymorphicModel
from safedelete import SOFT_DELETE
from safedelete.models import SafeDeleteModel

class CouponManager(models.Manager):
    def objects(self):
        return self.exclude(deleted_at__isnull=False)

class Coupon(PolymorphicModel, SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE

    PERCENTAGE = 'percent'
    DOLLARS = 'dollars'

    DISCOUNT_TYPE_CHOICES = [
        (PERCENTAGE, 'Percent off'),
        (DOLLARS, 'Dollars off'),
    ]

    code = models.CharField(max_length=6)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    discount_type = models.CharField(max_length=7, choices=DISCOUNT_TYPE_CHOICES)
    discount_amount = models.IntegerField()
    description = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
