import datetime
from django.conf import settings
import pytest

from staff.models.batch import Batch
from staff.models.course import Course
from staff.models.section import Section
from student.library.slack import Slack
from student.management.commands.create_slack_section_channels import Command

pytestmark = pytest.mark.django_db


@pytest.fixture()
def batch():
    COURSE_DURATION_IN_DAYS = 35
    start_date = datetime.date.today() + datetime.timedelta(days=settings.DAYS_BEFORE_BATCH_START_DATE)
    course = Course.objects.create(name=settings.CODING_BASICS)
    batch = Batch.objects.create(
        course=course,
        start_date=start_date,
        end_date=start_date + datetime.timedelta(COURSE_DURATION_IN_DAYS),
        capacity=18,
        sections=1
    )

    yield batch

def test_slack_section_channels_created_if_slack_channel_id_null(mocker, batch):
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

def test_slack_section_channels_not_created_if_slack_channel_id_exists(mocker, batch):
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
