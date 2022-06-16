from django.db import models
from django.conf import settings
from safedelete import SOFT_DELETE_CASCADE
from safedelete.models import SafeDeleteModel

from authentication.models import StudentUser
from staff.models.batch import Batch
from staff.models.section import Section


# null=True on student_user because this column was previously user
# Django requires default value for records existing before this new column
# null value makes most sense, although in reality this column will not be empty
class Enrolment(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    student_user = models.ForeignKey(StudentUser, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
