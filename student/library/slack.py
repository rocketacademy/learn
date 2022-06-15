from django.conf import settings
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
            print(api_response)
        except SlackApiError as error:
            print(f'Error creating channel: {error}')
