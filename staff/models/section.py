from django.db import models
from safedelete import SOFT_DELETE_CASCADE
from safedelete.models import SafeDeleteModel
from .batch import Batch

class Section(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    capacity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
