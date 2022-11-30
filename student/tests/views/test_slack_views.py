import pytest

from student.library.slack import Slack
from student.views.slack import team_join_event

pytestmark = pytest.mark.django_db


def test_team_join_event_calls_slack_methods_to_add_users_to_slack_channels_if_user_currently_enrolled(mocker, enrolment_factory):
    swe_fundamentals_enrolment = enrolment_factory(swe_fundamentals=True)
    swe_fundamentals_batch = swe_fundamentals_enrolment.batch
    swe_fundamentals_batch.slack_channel_id = 'C987654A'
    swe_fundamentals_batch.save()
    swe_fundamentals_section = swe_fundamentals_enrolment.section
    swe_fundamentals_section.slack_channel_id = 'C123456B'
    swe_fundamentals_section.save()
    student_user = swe_fundamentals_enrolment.student_user
    event = {
        'type': 'team_join',
        'user': {
            'profile': {
                'email': student_user.email
            },
            'id': 'U12345B'
        }
    }
    student_slack_user_id = event['user']['id']
    mocker.patch('student.library.slack.Slack.add_users_to_channel')

    team_join_event(event)

    Slack.add_users_to_channel.assert_has_calls(
        [
            mocker.call([student_slack_user_id], swe_fundamentals_batch.slack_channel_id),
            mocker.call([student_slack_user_id], swe_fundamentals_section.slack_channel_id)
        ]
    )
