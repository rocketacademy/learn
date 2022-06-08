from django.apps import apps
from django.conf import settings
from django.db import IntegrityError, transaction
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import stripe


@csrf_exempt
def config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)

@csrf_exempt
def create_checkout_session(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        request_body = json.loads(body_unicode)

        stripe.api_key = settings.STRIPE_SECRET_KEY

        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                metadata={
                    'payable_type': request_body['payable_type'],
                    'payable_id': request_body['payable_id'],
                },
                line_items=[
                    {
                        'name': request_body['payable_line_item_name'],
                        'quantity': 1,
                        'currency': settings.SINGAPORE_DOLLAR_CURRENCY,
                        'amount': request_body['payable_line_item_amount_in_cents'],
                    }
                ],
                mode='payment',
                success_url=settings.DOMAIN_URL + request_body['payment_success_path'],
                cancel_url=settings.DOMAIN_URL + request_body['payment_cancel_path'],
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as error:
            return JsonResponse({'error': str(error)})

@csrf_exempt
def webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as error:
        return HttpResponseBadRequest('Invalid payload')
    except stripe.error.SignatureVerificationError as error:
        return HttpResponseBadRequest('Invalid signature')

    if event['type'] == 'checkout.session.completed':
        event_data = event['data']['object']
        payable_id = int(event_data['metadata']['payable_id'])
        payable_object = apps.get_model('student', event_data['metadata']['payable_type']).objects.get(pk=payable_id)

        try:
            with transaction.atomic():
                payable_object.complete_transaction(event_data)
        except Exception as error:
            return HttpResponseServerError(error)
    # Save payment records for 'unpaid' payments, which are returned in expired checkout sessions
    elif event['type'] == 'checkout.session.expired':
        event_data = event['data']['object']
        payable_id = int(event_data['metadata']['payable_id'])
        payable_object = apps.get_model('student', event_data['metadata']['payable_type']).objects.get(pk=payable_id)

        try:
            with transaction.atomic():
                payable_object.record_stripe_payment(event_data)
        except IntegrityError:
            return HttpResponseServerError()
    return HttpResponse(status=200)