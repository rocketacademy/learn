import datetime
from django.conf import settings
from django.db import models
from django.utils.html import format_html
from safedelete import SOFT_DELETE_CASCADE
from safedelete.models import SafeDeleteModel

from staff.models.course import Course
from student.models.enrolment import Enrolment

class BatchManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class BasicsBatchManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True, course=Course.objects.get(name=Course.CODING_BASICS))

class BootcampBatchManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True, course=Course.objects.get(name=Course.CODING_BOOTCAMP))

class Batch(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    PART_TIME = 'part_time'
    FULL_TIME = 'full_time'

    TYPE_CHOICES = [
        (PART_TIME, 'Part-time'),
        (FULL_TIME, 'Full-time')
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    start_date = models.DateField(blank=False)
    end_date = models.DateField(blank=False)
    capacity = models.PositiveIntegerField(blank=False)
    sections = models.PositiveIntegerField(blank=False)
    slack_channel_id = models.CharField(max_length=20, null=True, blank=True)
    price = models.PositiveIntegerField(null=True)
    type = models.CharField(max_length=9, choices=TYPE_CHOICES, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = BatchManager()
    basics_objects = BasicsBatchManager()
    bootcamp_objects = BootcampBatchManager()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.number = Batch.next_number(self.course_id, self.type)

        if self.start_date >= self.end_date:
            raise ValueError('Batch end date should be after start date')

        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Batch {self.number}"

    @classmethod
    def next_number(self, course_id, type):
        course = Course.objects.get(pk=course_id)

        if course.name == Course.CODING_BASICS:
            if self.basics_objects.count() == 0:
                # 17 because this will be the first batch number when we launch Learn
                return 17
            return self.basics_objects.aggregate(models.Max('number'))['number__max'] + 1
        elif course.name == Course.CODING_BOOTCAMP:
            if type == Batch.PART_TIME:
                if self.bootcamp_objects.filter(type=Batch.PART_TIME).count() == 0:
                    print('parttime')
                    # 6 because this will be the first PTBC batch number when we launch bootcamp admin features
                    return 6
                return self.bootcamp_objects.aggregate(models.Max('number'))['number__max'] + 1
            elif type == Batch.FULL_TIME:
                if self.bootcamp_objects.filter(type=Batch.FULL_TIME).count() == 0:
                    print('fulltime')
                    # 10 because this will be the first FTBC batch number when we launch bootcamp admin features
                    return 10
                return self.bootcamp_objects.aggregate(models.Max('number'))['number__max'] + 1

    @staticmethod
    def html_formatted_batch_schedules(self):
        batchschedule_queryset = self.batchschedule_set.all()
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

    def ready_for_graduation(self):
        enrolments_pending_graduation = self.enrolment_set.filter(status=Enrolment.ENROLLED)

        return (self.end_date <= datetime.date.today()) and enrolments_pending_graduation.exists()

    def html_formatted_batch_price(self):
        original_price = self.price
        html_formatted_price = f"<span class='float-end d-none d-xl-block'>S${original_price}</span>"
        html_formatted_price += f"<div class='lh-lg d-xl-none my-10'>S${original_price}<div>"

        early_bird_discounted_price = original_price - self.early_bird_discount()
        if early_bird_discounted_price < original_price:
            html_formatted_price = f"<span class='float-end d-none d-xl-block'>S${early_bird_discounted_price}  <span id='original-price'><s>S${original_price}</s></span></span>"
            html_formatted_price += f"<div class='lh-lg d-xl-none'>S${early_bird_discounted_price}  <span id='original-price'><s>S${original_price}</s></span></div>"
        return format_html(html_formatted_price)

    def early_bird_discount(self):
        discount = 0
        if self.weeks_to_start() >= 3:
            discount = (self.weeks_to_start() - 2) * settings.CODING_BASICS_TIERED_DISCOUNT_PER_WEEK
            if discount > settings.CODING_BASICS_TIERED_DISCOUNT_CAP:
                discount = settings.CODING_BASICS_TIERED_DISCOUNT_CAP

        return discount

    def weeks_to_start(self):
        days_to_start_date = self.start_date - datetime.date.today()
        return days_to_start_date.days // 7

    def is_basics(self):
        return self.course.name == Course.CODING_BASICS

    def is_bootcamp(self):
        return self.course.name == Course.CODING_BOOTCAMP
