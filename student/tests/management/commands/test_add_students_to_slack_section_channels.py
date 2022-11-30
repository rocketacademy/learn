from datetime import date, timedelta
from django.conf import settings
import pytest

from student.management.commands.add_students_to_slack_section_channels import Command
from student.library.slack import Slack

pytestmark = pytest.mark.django_db


def test_only_picks_up_swe_fundamentals_batches_starting_in_7_days(mocker, enrolment_factory):
    start_date_7_days_from_now = date.today() + timedelta(days=settings.DAYS_BEFORE_BATCH_FOR_ADDING_STUDENTS_TO_SECTION_CHANNELS)
    first_swe_fundamentals_enrolment = enrolment_factory.create(swe_fundamentals=True, enrolled=True)
    swe_fundamentals_batch_starting_in_7_days = first_swe_fundamentals_enrolment.batch
    swe_fundamentals_batch_starting_in_7_days.start_date = start_date_7_days_from_now
    swe_fundamentals_batch_starting_in_7_days.end_date = start_date_7_days_from_now + timedelta(settings.SWE_FUNDAMENTALS_COURSE_DURATION_IN_DAYS)
    swe_fundamentals_batch_starting_in_7_days.save()
    first_swe_fundamentals_enrolment.section.slack_channel_id = 'C1234B'
    first_swe_fundamentals_enrolment.section.save()
    first_swe_fundamentals_enrolment.student_user.slack_user_id = 'U1234A'
    first_swe_fundamentals_enrolment.student_user.save()
    first_swe_fundamentals_enrolment.save()

    coding_basics_enrolment = enrolment_factory.create(coding_basics=True, enrolled=True)
    coding_basics_batch_starting_in_7_days = coding_basics_enrolment.batch
    coding_basics_batch_starting_in_7_days.start_date = start_date_7_days_from_now
    coding_basics_batch_starting_in_7_days.end_date = start_date_7_days_from_now + timedelta(settings.SWE_FUNDAMENTALS_COURSE_DURATION_IN_DAYS)
    coding_basics_batch_starting_in_7_days.save()

    start_date_8_days_from_now = date.today() + timedelta(days=settings.DAYS_BEFORE_BATCH_FOR_ADDING_STUDENTS_TO_SECTION_CHANNELS + 1)
    second_swe_fundamentals_enrolment = enrolment_factory.create(swe_fundamentals=True, enrolled=True)
    swe_fundamentals_batch_starting_in_8_days = second_swe_fundamentals_enrolment.batch
    swe_fundamentals_batch_starting_in_8_days.start_date = start_date_8_days_from_now
    swe_fundamentals_batch_starting_in_8_days.end_date = start_date_8_days_from_now + timedelta(settings.SWE_FUNDAMENTALS_COURSE_DURATION_IN_DAYS)
    swe_fundamentals_batch_starting_in_8_days.save()

    mocker.patch(
        'student.library.slack.Slack.add_users_to_channel'
    )

    Command().handle()

    Slack.add_users_to_channel.assert_called_once_with(
        [
            first_swe_fundamentals_enrolment.student_user.slack_user_id
        ],
        first_swe_fundamentals_enrolment.section.slack_channel_id
    )
