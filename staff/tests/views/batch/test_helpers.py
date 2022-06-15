import datetime
from django.conf import settings
import pytest
from unittest.mock import patch

from staff.models import Batch, Course, Section
from staff.views.batch import set_up_section

pytestmark = pytest.mark.django_db


@patch('student.library.slack.Slack.create_channel')
def test_set_up_section_creates_record_and_slack_channel(mock_create_channel):
    COURSE_DURATION_IN_DAYS = 35
    course = Course.objects.create(name=settings.CODING_BASICS)
    start_date = datetime.date.today()
    end_date = start_date + datetime.timedelta(COURSE_DURATION_IN_DAYS)
    section_capacity = 18
    no_of_sections = 1
    capacity = section_capacity * no_of_sections
    batch = Batch.objects.create(
        course=course,
        number=1,
        start_date=start_date,
        end_date=end_date,
        capacity=capacity,
        sections=no_of_sections
    )
    section_number = 1
    slack_channel_id = 'C12345A'
    mock_create_channel.return_value = slack_channel_id

    set_up_section(batch, section_number, section_capacity)

    assert Section.objects.count() == no_of_sections
    mock_create_channel.assert_called_once()
