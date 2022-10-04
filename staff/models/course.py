from django.db import models
from safedelete import SOFT_DELETE_CASCADE
from safedelete.models import SafeDeleteModel

class Course(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    CODING_BASICS = 'CODING_BASICS'
    CODING_BOOTCAMP = 'CODING_BOOTCAMP'

    NAME_CHOICES = [
        (CODING_BASICS, 'Coding Basics'),
        (CODING_BOOTCAMP, 'Coding Bootcamp')
    ]

    name = models.CharField(max_length=255, choices=NAME_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
