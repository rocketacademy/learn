from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from sendgrid.helpers.eventwebhook import EventWebhook, EventWebhookHeader
from sentry_sdk import capture_exception, capture_message

@csrf_exempt
def event_webhook(request):
    try:
        if is_valid_signature(request):
            return HttpResponse(status=200)
        return HttpResponseBadRequest(f"Could not process the request: {request.body.decode('utf-8')}")
    except Exception as error:
        capture_message(f"Exception when processing Sendgrid event: {error}")
        capture_exception(error)

        return HttpResponseServerError(str(error))

def is_valid_signature(request):
    event_webhook = EventWebhook()
    ec_public_key = event_webhook.convert_public_key_to_ecdsa(settings.SENDGRID_EVENT_WEBHOOK_VERIFICATION_KEY)

    return event_webhook.verify_signature(
        request.body.decode('utf-8'),
        request.headers[EventWebhookHeader.SIGNATURE],
        request.headers[EventWebhookHeader.TIMESTAMP],
        ec_public_key
    )
