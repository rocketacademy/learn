from datetime import date, timedelta
from django.conf import settings
import pytest

from staff.models.section import Section
from student.library.slack import Slack
from student.management.commands.create_slack_section_channels import Command

pytestmark = pytest.mark.django_db


def test_slack_section_channels_created_if_slack_channel_id_null(mocker, batch_factory):
    start_date = date.today() + timedelta(days=settings.DAYS_BEFORE_BATCH_FOR_CREATING_SECTION_CHANNELS)
    course_duration_in_days = 35
    batch = batch_factory.create(
        start_date=start_date,
        end_date=start_date + timedelta(days=course_duration_in_days)
    )
    section = Section.objects.create(
        batch=batch,
        number=1,
        capacity=18,
        slack_channel_id=None
    )
    slack_channel_name = f"{batch.number}-{section.number}"
    mocker.patch(
        'student.library.slack.Slack.create_channel',
        return_value='C1234567Q'
    )

    Command().handle()

    Slack.create_channel.assert_called_once_with(slack_channel_name)

def test_slack_section_channels_not_created_if_slack_channel_id_exists(mocker, batch_factory):
    batch = batch_factory.create()
    section = Section.objects.create(
        batch=batch,
        number=1,
        capacity=18,
        slack_channel_id='C1234567Q'
    )
    slack_channel_name = f"{batch.number}-{section.number}"
    mocker.patch(
        'student.library.slack.Slack.create_channel',
        return_value='C1234567Q'
    )

    Command().handle()

    assert not Slack.create_channel.called
