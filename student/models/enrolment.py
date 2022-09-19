from django.db import models
from django.conf import settings
from safedelete import SOFT_DELETE_CASCADE
from safedelete.models import SafeDeleteModel

from staff.models.batch import Batch
from staff.models.section import Section


# null=True on registration_id and student_user because these columns have been changed
# Django requires default value for records existing before this new column
# null value makes most sense, although in reality this column will not be empty
class Enrolment(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    ENROLLED = 'ENROLLED'
    PASSED = 'PASSED'
    FAILED = 'FAILED'

    STATUS_CHOICES = [
        (ENROLLED, 'Enrolled'),
        (PASSED, 'Passed'),
        (FAILED, 'Failed')
    ]

    registration = models.ForeignKey('student.Registration', on_delete=models.CASCADE, null=True)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    student_user = models.ForeignKey('authentication.StudentUser', on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=ENROLLED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
