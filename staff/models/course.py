from django.db import models
from django.conf import settings
from safedelete import SOFT_DELETE_CASCADE
from safedelete.models import SafeDeleteModel

class Course(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    NAME_CHOICES = [
        (settings.CODING_BASICS, 'Coding Basics')
    ]

    name = models.CharField(max_length=255, choices=NAME_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
