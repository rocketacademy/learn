import pytest
from unittest.mock import patch

from staff.views.batch import create_batch_slack_channel

pytestmark = pytest.mark.django_db


@patch('student.library.slack.Slack.create_channel')
def test_create_batch_slack_channel(mock_create_channel, batch_factory):
    batch = batch_factory.create()
    slack_channel_id = 'C12345A'
    mock_create_channel.return_value = slack_channel_id

    create_batch_slack_channel(batch)

    mock_create_channel.assert_called_once()
    assert batch.slack_channel_id == slack_channel_id
