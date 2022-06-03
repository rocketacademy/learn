from django.db import models
from django.utils.html import format_html
from safedelete import SOFT_DELETE_CASCADE
from safedelete.models import SafeDeleteModel

from staff.models.course import Course

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

    def __str__(self):
        return f"Batch {self.number}"

    @classmethod
    def next_number(self, course_id):
        if self.objects.count() == 0:
            return 1
        return self.objects.filter(course__id=course_id).aggregate(models.Max('number'))['number__max'] + 1

    @staticmethod
    def html_formatted_batch_schedules(self):
        batchschedule_queryset = self.batchschedule_set.order_by('iso_week_day')
        html_formatted_batch_schedules = ""

        for batch_schedule in batchschedule_queryset:
            html_formatted_batch_schedules += f"<small>{batch_schedule}</small><br>"

        return format_html(html_formatted_batch_schedules)

    def next_enrollable_section(self):
        ordered_sections = self.section_set.all().order_by('number')

        for section in ordered_sections:
            if not section.fully_enrolled():
                return section
        return None

    def fully_enrolled(self):
        if self.enrolment_set.count() >= self.capacity and self.next_enrollable_section() is None:
            return True
        return False
