from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from sentry_sdk import capture_message
import threading

from authentication.models import StudentUser
from student.library.slack import Slack


@csrf_exempt
def event_hook(request):
    request_body_json_dict = json.loads(request.body.decode('utf-8'))

    if 'type' in request_body_json_dict and request_body_json_dict['type'] == 'url_verification':
        return JsonResponse({'challenge': request_body_json_dict['challenge']}, safe=False)

    if 'event' in request_body_json_dict:
        event = request_body_json_dict['event']

        if event['type'] == 'team_join':
            thread = threading.Thread(target=team_join_event, args=(event,))
            thread.start()

            return HttpResponse(status=200)

def team_join_event(event):
    slack_user_email = event['user']['profile']['email']
    slack_user_id = event['user']['id']
    student_user = StudentUser.objects.filter(email=slack_user_email).first()

    if student_user:
        try:
            student_user.slack_user_id = slack_user_id
            student_user.save()

            slack_client = Slack()
            for batch in student_user.current_enrolled_basics_batches() or []:
                if batch.slack_channel_id:
                    slack_client.add_users_to_channel([slack_user_id], batch.slack_channel_id)
            for section in student_user.current_enrolled_sections() or []:
                if section.slack_channel_id:
                    slack_client.add_users_to_channel([slack_user_id], section.slack_channel_id)
        except Exception as error:
            capture_message(error)
    else:
        capture_message(f'User with email {slack_user_email} does not exist in Learn')
