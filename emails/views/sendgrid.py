from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
import json
from sendgrid.helpers.eventwebhook import EventWebhook, EventWebhookHeader
from sentry_sdk import capture_exception, capture_message

from emails.models import SendgridEvent
from emails.models.sendgrid_events.bounce_sendgrid_event import BounceSendgridEvent
from emails.models.sendgrid_events.deferred_sendgrid_event import DeferredSendgridEvent
from emails.models.sendgrid_events.delivered_sendgrid_event import DeliveredSendgridEvent
from emails.models.sendgrid_events.dropped_sendgrid_event import DroppedSendgridEvent
from emails.models.sendgrid_events.processed_sendgrid_event import ProcessedSendgridEvent


@csrf_exempt
def event_webhook(request):
    try:
        if is_valid_signature(request):
            event = json.loads(request.body)

            for event in event:
                process(event)

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

def process(event):
    match event['event']:
        case SendgridEvent.PROCESSED:
            ProcessedSendgridEvent.objects.create(
                emailable_id=event['emailable_id'],
                emailable_type=event['emailable_type'],
                recipient_email=event['email'],
                timestamp=event['timestamp'],
                sg_event_id=event['sg_event_id'],
                sg_message_id=event['sg_message_id'],
                category=event['category'],
                smtp_id=event['smtp-id']
            )
        case SendgridEvent.DROPPED:
            DroppedSendgridEvent.objects.create(
                emailable_id=event['emailable_id'],
                emailable_type=event['emailable_type'],
                recipient_email=event['email'],
                timestamp=event['timestamp'],
                sg_event_id=event['sg_event_id'],
                sg_message_id=event['sg_message_id'],
                category=event['category'],
                smtp_id=event['smtp-id'],
                reason=event['reason'],
                status=event['status']
            )
        case SendgridEvent.DELIVERED:
            DeliveredSendgridEvent.objects.create(
                emailable_id=event['emailable_id'],
                emailable_type=event['emailable_type'],
                recipient_email=event['email'],
                timestamp=event['timestamp'],
                sg_event_id=event['sg_event_id'],
                sg_message_id=event['sg_message_id'],
                category=event['category'],
                smtp_id=event['smtp-id'],
                ip=event['ip']
            )
        case SendgridEvent.DEFERRED:
            DeferredSendgridEvent.objects.create(
                emailable_id=event['emailable_id'],
                emailable_type=event['emailable_type'],
                recipient_email=event['email'],
                timestamp=event['timestamp'],
                sg_event_id=event['sg_event_id'],
                sg_message_id=event['sg_message_id'],
                category=event['category'],
                smtp_id=event['smtp-id'],
                ip=event['ip'],
                attempt=event['attempt']
            )
        case SendgridEvent.BOUNCE:
            BounceSendgridEvent.objects.create(
                emailable_id=event['emailable_id'],
                emailable_type=event['emailable_type'],
                recipient_email=event['email'],
                timestamp=event['timestamp'],
                sg_event_id=event['sg_event_id'],
                sg_message_id=event['sg_message_id'],
                category=event['category'],
                bounce_classification=event['bounce_classification'],
                smtp_id=event['smtp-id'],
                ip=event['ip'],
                reason=event['reason'],
                status=event['status']
            )
