from datetime import date, timedelta
from django.conf import settings
from django.core.management.base import BaseCommand

from staff.models import Batch, Section
from student.library.slack import Slack


class Command(BaseCommand):
    help = 'Creates Slack section channels before course begins'

    def handle(self, *args, **options):
        batch_start_date = date.today() + timedelta(days=settings.DAYS_BEFORE_BATCH_FOR_CREATING_SECTION_CHANNELS)
        slack_client = Slack()

        batches_about_to_begin = Batch.swe_fundamentals_objects.filter(start_date=batch_start_date)
        for batch in batches_about_to_begin:
            section_queryset = Section.objects.filter(batch__id=batch.id).filter(slack_channel_id__isnull=True)

            for section in section_queryset:
                slack_channel_name = f"{batch.number}-{section.number}"
                self.stdout.write(f"Creating slack channel {slack_channel_name}")

                slack_channel_id = slack_client.create_channel(slack_channel_name)
                section.slack_channel_id = slack_channel_id
                section.save()
