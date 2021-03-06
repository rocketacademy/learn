import datetime
from django.conf import settings
import pytest
from authentication.models import StudentUser

from staff.models import Batch, Course, Section
from student.management.commands.add_students_to_slack_section_channels import Command
from student.library.slack import Slack
from student.models.enrolment import Enrolment
from student.models.registration import Registration

pytestmark = pytest.mark.django_db
COURSE_DURATION_IN_DAYS = 35


def test_only_picks_up_batches_starting_in_7_days(mocker):
    today = datetime.date.today()
    course = Course.objects.create(name=settings.CODING_BASICS)
    start_date_7_days_from_now = today + datetime.timedelta(days=settings.DAYS_BEFORE_BATCH_FOR_ADDING_STUDENTS_TO_SECTION_CHANNELS)
    batch_starting_in_7_days = Batch.objects.create(
        course=course,
        start_date=start_date_7_days_from_now,
        end_date=start_date_7_days_from_now + datetime.timedelta(COURSE_DURATION_IN_DAYS),
        capacity=18,
        sections=1
    )
    section = Section.objects.create(
        batch=batch_starting_in_7_days,
        number=1,
        capacity=18,
        slack_channel_id='C1234B'
    )
    start_date_8_days_from_now = today + datetime.timedelta(days=settings.DAYS_BEFORE_BATCH_FOR_ADDING_STUDENTS_TO_SECTION_CHANNELS + 1)
    batch_starting_in_8_days = Batch.objects.create(
        course=course,
        start_date=start_date_8_days_from_now,
        end_date=start_date_8_days_from_now + datetime.timedelta(COURSE_DURATION_IN_DAYS),
        capacity=18,
        sections=1
    )
    registration = Registration.objects.create(
        course=course,
        batch=batch_starting_in_7_days,
        first_name='Firstname',
        last_name='Lastname',
        email='student@example.com',
        country_of_residence='SG',
        referral_channel='word_of_mouth',
    )
    student_user = StudentUser.objects.create_user(
        email='student@example.com',
        first_name='Firstname',
        last_name='Lastname',
        password=settings.PLACEHOLDER_PASSWORD,
    )
    student_user.slack_user_id = 'U1234A'
    student_user.save()
    enrolment = Enrolment.objects.create(
        registration=registration,
        batch=batch_starting_in_7_days,
        section=section,
        student_user=student_user,
    )
    mocker.patch(
        'student.library.slack.Slack.add_users_to_channel'
    )

    Command().handle()

    Slack.add_users_to_channel.assert_called_once_with([student_user.slack_user_id], section.slack_channel_id)
