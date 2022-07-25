from datetime import date, timedelta
from django.conf import settings
import pytest

from authentication.models import StudentUser
from staff.models import Batch, Course, Section
from student.library.slack import Slack
from student.models.enrolment import Enrolment
from student.models.registration import Registration
from student.views.slack import team_join_event

pytestmark = pytest.mark.django_db

email = 'email@example.com'
first_name = 'Student'
last_name = 'Name'


@pytest.fixture()
def student_user():
    student_user = StudentUser.objects.create_user(
        email=email,
        first_name=first_name,
        last_name=last_name,
        password=settings.PLACEHOLDER_PASSWORD,
    )

    yield student_user

@pytest.fixture()
def enrolment():
    course = Course.objects.create(name=settings.CODING_BASICS)
    batch = Batch.objects.create(
        course=course,
        number=1,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=1),
        capacity=1,
        sections=1,
        slack_channel_id='C987654A',
    )
    section = Section.objects.create(
        batch=batch,
        number=1,
        capacity=1,
        slack_channel_id='C123456B',
    )
    registration = Registration.objects.create(
        course=course,
        batch=batch,
        first_name=first_name,
        last_name=last_name,
        email=email,
        country_of_residence='SG',
        referral_channel='word_of_mouth'
    )
    student_user = StudentUser.objects.get(email=registration.email)
    enrolment = Enrolment.objects.create(
        registration=registration,
        batch=batch,
        section=section,
        student_user=student_user
    )

    yield enrolment

def test_team_join_event_calls_slack_methods_to_add_users(mocker, student_user, enrolment):
    event = {
        'type': 'team_join',
        'user': {
            'profile': {
                'email': email
            },
            'id': 'U12345B'
        }
    }
    student_slack_user_id = event['user']['id']
    mocker.patch('student.library.slack.Slack.add_users_to_channel')

    team_join_event(event)

    Slack.add_users_to_channel.assert_called_once_with([student_slack_user_id], enrolment.batch.slack_channel_id)
