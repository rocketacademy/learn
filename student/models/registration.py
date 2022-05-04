from django.db import models
from safedelete import SOFT_DELETE_CASCADE
from safedelete.models import SafeDeleteModel
from ...staff.models.course import Course
from ...staff.models.batch import Batch
from payments.payment import Payment


class Registration(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=254, unique=True)
    country_of_residence = models.CharField(max_length=255)
    referral_channel = models.CharField(max_length=255)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(auto_now=True)
