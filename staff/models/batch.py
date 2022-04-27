from django.db import models
from safedelete import SOFT_DELETE_CASCADE
from safedelete.models import SafeDeleteModel
from .course import Course

class Batch(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    capacity = models.PositiveIntegerField()
    sections = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        batches_queryset = Batch.objects.filter(course__id=self.course_id)
        latest_batch = batches_queryset.order_by('number').last()

        if latest_batch is None:
            self.number = 1
        else:
            self.number = latest_batch.number + 1

        if self.start_date >= self.end_date:
            raise ValueError('Batch end date should be after start date')

        return super().save(*args, **kwargs)