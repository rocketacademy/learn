from django.conf import settings
from django.db import IntegrityError, transaction
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
    if is_valid_signature(request):
        events = json.loads(request.body)

        for event in events:
            process(event)

        return HttpResponse(status=200)
    return HttpResponseBadRequest(f"Could not process the request: {request.body.decode('utf-8')}")

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
            if not ProcessedSendgridEvent.objects.filter(
                emailable_id=event['emailable_id'],
                emailable_type=event['emailable_type'],
                recipient_email=event['email'],
                timestamp=event['timestamp'],
                sg_event_id=event['sg_event_id'],
                sg_message_id=event['sg_message_id'],
                sg_template_id=event['sg_template_id'],
                sg_template_name=event['sg_template_name'],
            ).exists():
                try:
                    with transaction.atomic():
                        ProcessedSendgridEvent.objects.create(
                            emailable_id=event['emailable_id'],
                            emailable_type=event['emailable_type'],
                            recipient_email=event['email'],
                            timestamp=event['timestamp'],
                            sg_event_id=event['sg_event_id'],
                            sg_message_id=event['sg_message_id'],
                            sg_template_id=event['sg_template_id'],
                            sg_template_name=event['sg_template_name'],
                        )

                    return HttpResponse(status=200)
                except IntegrityError as error:
                    capture_message(
                        f"Error processing Sendgrid {event['event']} event for {event['emailable_type']}-{event['emailable_id']}: {error}"
                    )
                    capture_exception(error)

                    return HttpResponseServerError(error)
        case SendgridEvent.DROPPED:
            if not DroppedSendgridEvent.objects.filter(
                emailable_id=event['emailable_id'],
                emailable_type=event['emailable_type'],
                recipient_email=event['email'],
                timestamp=event['timestamp'],
                sg_event_id=event['sg_event_id'],
                sg_message_id=event['sg_message_id'],
                sg_template_id=event['sg_template_id'],
                sg_template_name=event['sg_template_name'],
                reason=event['reason'],
            ).exists():
                try:
                    with transaction.atomic():
                        DroppedSendgridEvent.objects.create(
                            emailable_id=event['emailable_id'],
                            emailable_type=event['emailable_type'],
                            recipient_email=event['email'],
                            timestamp=event['timestamp'],
                            sg_event_id=event['sg_event_id'],
                            sg_message_id=event['sg_message_id'],
                            sg_template_id=event['sg_template_id'],
                            sg_template_name=event['sg_template_name'],
                            reason=event['reason'],
                        )
                    return HttpResponse(status=200)
                except Exception as error:
                    capture_message(
                        f"Error processing Sendgrid {event['event']} event for {event['emailable_type']}-{event['emailable_id']}: {error}"
                    )
                    capture_exception(error)

                    return HttpResponseServerError(error)
        case SendgridEvent.DELIVERED:
            if not DeliveredSendgridEvent.objects.filter(
                emailable_id=event['emailable_id'],
                emailable_type=event['emailable_type'],
                recipient_email=event['email'],
                timestamp=event['timestamp'],
                sg_event_id=event['sg_event_id'],
                sg_message_id=event['sg_message_id'],
                sg_template_id=event['sg_template_id'],
                sg_template_name=event['sg_template_name']
            ).exists():
                try:
                    with transaction.atomic():
                        DeliveredSendgridEvent.objects.create(
                            emailable_id=event['emailable_id'],
                            emailable_type=event['emailable_type'],
                            recipient_email=event['email'],
                            timestamp=event['timestamp'],
                            sg_event_id=event['sg_event_id'],
                            sg_message_id=event['sg_message_id'],
                            sg_template_id=event['sg_template_id'],
                            sg_template_name=event['sg_template_name']
                        )
                    return HttpResponse(status=200)
                except Exception as error:
                    capture_message(
                        f"Error processing Sendgrid {event['event']} event for {event['emailable_type']}-{event['emailable_id']}: {error}")
                    capture_exception(error)

                    return HttpResponseServerError(error)
        case SendgridEvent.DEFERRED:
            if not DeferredSendgridEvent.objects.filter(
                emailable_id=event['emailable_id'],
                emailable_type=event['emailable_type'],
                recipient_email=event['email'],
                timestamp=event['timestamp'],
                sg_event_id=event['sg_event_id'],
                sg_message_id=event['sg_message_id'],
                sg_template_id=event['sg_template_id'],
                sg_template_name=event['sg_template_name'],
                attempt=event['attempt']
            ).exists():
                try:
                    DeferredSendgridEvent.objects.create(
                        emailable_id=event['emailable_id'],
                        emailable_type=event['emailable_type'],
                        recipient_email=event['email'],
                        timestamp=event['timestamp'],
                        sg_event_id=event['sg_event_id'],
                        sg_message_id=event['sg_message_id'],
                        sg_template_id=event['sg_template_id'],
                        sg_template_name=event['sg_template_name'],
                        attempt=event['attempt']
                    )
                except Exception as error:
                    capture_message(
                        f"Error processing Sendgrid {event['event']} event for {event['emailable_type']}-{event['emailable_id']}: {error}"
                    )
                    capture_exception(error)

                    return HttpResponseServerError(error)
        case SendgridEvent.BOUNCE:
            if not BounceSendgridEvent.objects.filter(
                emailable_id=event['emailable_id'],
                emailable_type=event['emailable_type'],
                recipient_email=event['email'],
                timestamp=event['timestamp'],
                sg_event_id=event['sg_event_id'],
                sg_message_id=event['sg_message_id'],
                sg_template_id=event['sg_template_id'],
                sg_template_name=event['sg_template_name'],
                bounce_classification=event['bounce_classification'],
                reason=event['reason'],
            ).exists():
                try:
                    BounceSendgridEvent.objects.create(
                        emailable_id=event['emailable_id'],
                        emailable_type=event['emailable_type'],
                        recipient_email=event['email'],
                        timestamp=event['timestamp'],
                        sg_event_id=event['sg_event_id'],
                        sg_message_id=event['sg_message_id'],
                        sg_template_id=event['sg_template_id'],
                        sg_template_name=event['sg_template_name'],
                        bounce_classification=event['bounce_classification'],
                        reason=event['reason'],
                    )
                except Exception as error:
                    capture_message(
                        f"Error processing Sendgrid {event['event']} event for {event['emailable_type']}-{event['emailable_id']}: {error}"
                    )
                    capture_exception(error)

                    return HttpResponseServerError(error)
