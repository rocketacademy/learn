from django.db import models
from safedelete import SOFT_DELETE_CASCADE
from safedelete.models import SafeDeleteModel

from .batch import Batch

MONDAY = 'MON'
TUESDAY = 'TUE'
WEDNESDAY = 'WED'
THURSDAY = 'THU'
FRIDAY = 'FRI'
SATURDAY = 'SAT'
SUNDAY = 'SUN'

DAY_CHOICES = [
    (MONDAY, 'Monday'),
    (TUESDAY, 'Tuesday'),
    (WEDNESDAY, 'Wednesday'),
    (THURSDAY, 'Thursday'),
    (FRIDAY, 'Friday'),
    (SATURDAY, 'Saturday'),
    (SUNDAY, 'Sunday')
]

class BatchScheduleManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by('iso_week_day')

class BatchSchedule(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    iso_week_day = models.IntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = BatchScheduleManager()

    def __str__(self):
        day_choices_dict = dict(DAY_CHOICES)
        formatted_start_time = self.start_time.strftime("%-I:%M%p")
        formatted_end_time = self.end_time.strftime("%-I:%M%p")

        return f"{day_choices_dict[self.day]}s, {formatted_start_time} to {formatted_end_time}"
