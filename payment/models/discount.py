from django.conf import settings
from django.db import models
from polymorphic.models import PolymorphicModel


class Discount(PolymorphicModel):
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def dollar_amount(self):
        return self.amount / settings.CENTS_PER_DOLLAR
