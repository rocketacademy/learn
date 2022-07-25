from datetime import date, timedelta
from django.conf import settings
from django.core.management.base import BaseCommand

from authentication.models import StudentUser
from staff.models import Batch, Section
from student.library.slack import Slack
from student.models.enrolment import Enrolment


class Command(BaseCommand):
    help = f"Add students to Slack section channels {settings.DAYS_BEFORE_BATCH_FOR_ADDING_STUDENTS_TO_SECTION_CHANNELS} days before course begins"

    def handle(self, *args, **options):
        batch_start_date = date.today() + timedelta(days=settings.DAYS_BEFORE_BATCH_FOR_ADDING_STUDENTS_TO_SECTION_CHANNELS)
        batch_ids = Batch.objects.filter(start_date=batch_start_date).values_list('pk', flat=True)
        section_ids = Enrolment.objects.filter(batch_id__in=batch_ids).values_list('section_id', flat=True)
        slack_client = Slack()

        for section_id in section_ids:
            slack_section_channel_id = Section.objects.get(pk=section_id).slack_channel_id
            slack_user_ids = list(StudentUser.objects.filter(pk__in=(Enrolment.objects.filter(section_id=section_id).values('student_user_id'))).values_list('slack_user_id', flat=True))
            self.stdout.write(f"Adding users {slack_user_ids} to {slack_section_channel_id}")

            slack_client.add_users_to_channel(slack_user_ids, slack_section_channel_id)
