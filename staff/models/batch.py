from django.db import models
from safedelete import SOFT_DELETE_CASCADE
from safedelete.models import SafeDeleteModel
from .course import Course

class Batch(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    start_date = models.DateField(blank=False)
    end_date = models.DateField(blank=False)
    capacity = models.PositiveIntegerField(blank=False)
    sections = models.PositiveIntegerField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        batch_queryset = Batch.objects.filter(course__id=self.course_id)
        latest_batch = batch_queryset.order_by('number').last()

        if latest_batch is None:
            self.number = 1
        else:
            self.number = latest_batch.number + 1

        if self.start_date >= self.end_date:
            raise ValueError('Batch end date should be after start date')

        return super().save(*args, **kwargs)
