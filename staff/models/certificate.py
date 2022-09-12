from django.db import models
from django.utils.crypto import get_random_string
from safedelete import SOFT_DELETE_CASCADE
from safedelete.models import SafeDeleteModel

from authentication.models import StudentUser
from staff.models.course import Course


class Certificate(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    credential = models.CharField(max_length=12, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student_user = models.ForeignKey(StudentUser, on_delete=models.CASCADE)
    graduation_date = models.DateField()

    def save(self, *args, **kwargs):
        # only validate if object is new
        # because we should not validate the certificate's credential other attributes are updated
        if not self.pk:
            random_string = get_random_string(length=12)

            while Certificate.objects.filter(credential=random_string).exists():
                random_string = get_random_string(length=12)

            self.credential = random_string.upper()

        return super().save(*args, **kwargs)
