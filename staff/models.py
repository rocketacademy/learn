from django.db import models

class Course(models.Model):
    CODING_BASICS = 'CODING_BASICS'

    NAME_CHOICES = [
        (CODING_BASICS, 'Coding Basics')
    ]

    name = models.CharField(max_length=255, choices=NAME_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Batch(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    capacity = models.PositiveIntegerField()
    sections = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        latest_batch = Batch.objects.filter(course__id=self.course_id).order_by('number').last()

        if latest_batch == None:
            self.number = 1
        else:
            self.number = latest_batch.number + 1

        if self.start_date >= self.end_date:
            raise ValueError('Batch end date should be after start date')

        return super().save(*args, **kwargs)

class BatchSchedule(models.Model):
    MONDAY = 'MON'
    TUESDAY = 'TUES'
    WEDNESDAY = 'WED'
    THURSDAY = 'THUR'
    FRIDAY = 'FRI'
    SATURDAY = 'SAT'
    SUNDAY = 'SUN'

    COURSE_DAY_CHOICES = [
        (MONDAY, 'Monday'),
        (TUESDAY, 'Tuesday'),
        (WEDNESDAY, 'Wednesday'),
        (THURSDAY, 'Thursday'),
        (FRIDAY, 'Friday'),
        (SATURDAY, 'Saturday'),
        (SUNDAY, 'Sunday')
    ]

    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    course_day = models.CharField(max_length=4, choices=COURSE_DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
