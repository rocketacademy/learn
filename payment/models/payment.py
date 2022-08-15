from django.db import models
from polymorphic.models import PolymorphicModel
from safedelete import SOFT_DELETE_CASCADE
from safedelete.models import SafeDeleteModel


class Payment(PolymorphicModel, SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    payable_id = models.IntegerField()
    payable_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
