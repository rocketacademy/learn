from django.conf import settings
from sentry_sdk import capture_exception, capture_message
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class Slack:
    def __init__(self):
        self.client = WebClient(token=settings.SLACK_USER_OAUTH_TOKEN)

    def create_channel(self, name):
        try:
            api_response = self.client.conversations_create(
                name=name
            )

            return api_response['channel']['id']
        except SlackApiError as error:
            capture_message('Error creating channel')
            capture_exception(error)

    def add_users_to_channel(self, slack_user_ids, slack_channel_id):
        try:
            api_response = self.client.conversations_invite(
                users=slack_user_ids,
                channel=slack_channel_id
            )

            return api_response
        except SlackApiError as error:
            capture_message('Error inviting user(s) to channel')
            capture_exception(error)
