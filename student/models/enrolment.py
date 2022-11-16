from django.db import models
from safedelete import SOFT_DELETE_CASCADE
from safedelete.models import SafeDeleteModel


ENROLLED = 'ENROLLED'
PASSED = 'PASSED'
FAILED = 'FAILED'
DEFERRED = 'DEFERRED'

class EnrolmentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=ENROLLED) | super().get_queryset().filter(status=PASSED) | super().get_queryset().filter(status=FAILED)

# null=True on registration_id and student_user because these columns have been changed
# Django requires default value for records existing before this new column
# null value makes most sense, although in reality this column will not be empty
class Enrolment(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    ENROLLED = ENROLLED
    PASSED = PASSED
    FAILED = FAILED
    DEFERRED = DEFERRED

    STATUS_CHOICES = [
        (ENROLLED, 'Enrolled'),
        (PASSED, 'Passed'),
        (FAILED, 'Failed'),
        (DEFERRED, 'Deferred')
    ]

    registration = models.ForeignKey('student.Registration', on_delete=models.CASCADE, null=True)
    batch = models.ForeignKey('staff.Batch', on_delete=models.CASCADE)
    section = models.ForeignKey('staff.Section', on_delete=models.CASCADE)
    student_user = models.ForeignKey('authentication.StudentUser', on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=ENROLLED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = EnrolmentManager()
