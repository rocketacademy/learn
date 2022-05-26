from django.db import models
from django.conf import settings
from safedelete import SOFT_DELETE_CASCADE
from safedelete.models import SafeDeleteModel

from staff.models.batch import Batch
from staff.models.section import Section


class Enrolment(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
