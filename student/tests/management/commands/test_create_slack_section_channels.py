from datetime import date, timedelta
from django.conf import settings
import pytest

from student.library.slack import Slack
from student.management.commands.create_slack_section_channels import Command

pytestmark = pytest.mark.django_db

start_date = date.today() + timedelta(days=settings.DAYS_BEFORE_BATCH_FOR_CREATING_SECTION_CHANNELS)
end_date = start_date + timedelta(days=settings.SWE_FUNDAMENTALS_COURSE_DURATION_IN_DAYS)


def test_slack_section_channels_created_if_slack_channel_id_null(mocker, batch_factory, section_factory):
    batch = batch_factory.create(
        start_date=start_date,
        end_date=end_date,
        swe_fundamentals=True
    )
    section = section_factory.create(
        batch=batch,
        slack_channel_id_exists=False
    )
    mocker.patch(
        'student.library.slack.Slack.create_channel',
        return_value='C1234567Q'
    )

    Command().handle()

    Slack.create_channel.assert_called_once_with(f"{batch.number}-{section.number}")

def test_slack_section_channels_not_created_if_slack_channel_id_exists(mocker, batch_factory, section_factory):
    batch = batch_factory.create(
        start_date=start_date,
        end_date=end_date,
        swe_fundamentals=True
    )
    section_factory.create(
        batch=batch,
        slack_channel_id_exists=True
    )
    mocker.patch(
        'student.library.slack.Slack.create_channel',
        return_value='C1234567Q'
    )

    Command().handle()

    Slack.create_channel.assert_not_called()
