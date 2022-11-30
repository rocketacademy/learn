import datetime
from django.db import models
from django.contrib.auth import get_user_model

from staff.models import Batch, Section
import student

User = get_user_model()


class StudentUser(User):
    hubspot_contact_id = models.IntegerField(null=True, blank=True)
    slack_user_id = models.CharField(max_length=20, null=True, blank=True)

    def current_enrolled_swe_fundamentals_batches(self):
        enrolments = student.models.enrolment.Enrolment.objects.filter(student_user_id=self.id, status=student.models.enrolment.Enrolment.ENROLLED)
        current_enrolled_swe_fundamentals_batches = Batch.swe_fundamentals_objects.filter(end_date__gte=datetime.date.today()).filter(enrolment__in=enrolments)

        return current_enrolled_swe_fundamentals_batches

    def current_enrolled_sections(self):
        enrolments = student.models.enrolment.Enrolment.objects.filter(student_user_id=self.id, status=student.models.enrolment.Enrolment.ENROLLED)
        section_ids = enrolments.values_list('section_id', flat=True)
        sections = Section.objects.filter(pk__in=section_ids).filter(batch__end_date__gte=datetime.date.today())

        return sections
