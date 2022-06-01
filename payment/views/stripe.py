from django.conf import settings
from django.db import IntegrityError, transaction
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import stripe

from payment.models import StripePayment


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
        return HttpResponseBadRequest
    except stripe.error.SignatureVerificationError as error:
        return HttpResponseBadRequest

    if event['type'] == 'checkout.session.completed':
        event_data = event['data']['object']

        try:
            with transaction.atomic():
                StripePayment.objects.create(
                    payable_type=event_data['metadata']['payable_type'],
                    payable_id=event_data['metadata']['payable_id'],
                    intent=event_data['payment_intent'],
                    customer=event_data['customer'],
                    customer_email=event_data['customer_details']['email'],
                    amount=event_data['amount_total'],
                    currency=event_data['currency'],
                    status=event_data['payment_status']
                )
        except IntegrityError:
            return HttpResponseServerError
    return HttpResponse(status=200)
