from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
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
        current_enrolled_batches = student_user.current_enrolled_batches()
        student_user.slack_user_id = slack_user_id
        student_user.save()

        if current_enrolled_batches:
            slack_client = Slack()
            slack_user_ids = [slack_user_id]

            for batch in current_enrolled_batches:
                slack_client.add_users_to_channel(slack_user_ids, batch.slack_channel_id)
    else:
        print(f'User with email {slack_user_email} does not exist in Learn')
