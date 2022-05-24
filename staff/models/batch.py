from django.db import models
from django.utils.html import format_html, mark_safe
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
        if not self.pk:
            self.number = Batch.next_number(self.course_id)
        elif Batch.objects.count() == 0:
            self.number = 1

        if self.start_date >= self.end_date:
            raise ValueError('Batch end date should be after start date')

        return super().save(*args, **kwargs)

    @classmethod
    def next_number(self, course_id):
        if self.objects.count() == 0:
            return 1
        return self.objects.filter(course__id=course_id).aggregate(models.Max('number'))['number__max'] + 1

    def registration_form_display(self):
        duration = f'{self.start_date.strftime("%d %B")} to {self.end_date.strftime("%d %B")}'

        return format_html(
            "<h6>Batch {}</h6><div>{}</div>",
            self.number,
            duration,
        )

    def __str__(self):
        return self.registration_form_display()
