from django.db import models
from polymorphic.models import PolymorphicModel


class Payment(PolymorphicModel):
    payable_id = models.IntegerField()
    payable_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
