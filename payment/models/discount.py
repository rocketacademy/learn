from django.db import models
from polymorphic.models import PolymorphicModel


class Discount(PolymorphicModel):
    original_amount = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
