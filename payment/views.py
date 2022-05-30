from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import stripe

from .models import StripePayment


@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)

@csrf_exempt
def create_checkout_session(request, payable_type, payable_id):
    if request.method == 'GET':
        stripe.api_key = settings.STRIPE_SECRET_KEY
        domain_url = settings.DOMAIN_URL
        singapore_dollar_currency = settings.SINGAPORE_DOLLAR_CURRENCY

        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                metadata={
                    'payable_type': payable_type,
                    'payable_id': payable_id,
                },
                line_items=[
                    {
                        'name': 'Registration for Coding Basics',
                        'quantity': 1,
                        'currency': singapore_dollar_currency,
                        'amount': '19900',
                    }
                ],
                mode='payment',
                success_url=domain_url + '/student/basics/register/confirmation/',
                cancel_url=domain_url + '/student/basics/register/',
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as error:
            return JsonResponse({'error': str(error)})

@csrf_exempt
def stripe_webhook(request):
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

    return HttpResponse(status=200)
