import datetime
from django.db import models
from django.contrib.auth import get_user_model

from staff.models import Batch, Section
import student

User = get_user_model()


class StudentUser(User):
    hubspot_contact_id = models.IntegerField(null=True, blank=True)
    slack_user_id = models.CharField(max_length=20, null=True, blank=True)

    def current_enrolled_batches(self):
        enrolments = student.models.enrolment.Enrolment.objects.filter(student_user_id=self.id)
        current_enrolled_batches = Batch.objects.filter(end_date__gte=datetime.date.today()).filter(enrolment__in=enrolments)

        return current_enrolled_batches

    def current_enrolled_sections(self):
        enrolments = student.models.enrolment.Enrolment.objects.filter(student_user_id=self.id)
        section_ids = enrolments.values_list('section_id', flat=True)
        sections = Section.objects.filter(pk__in=section_ids).filter(batch__end_date__gte=datetime.date.today())

        return sections
