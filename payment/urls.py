from django.urls import path
from payment.views import stripe

urlpatterns = [
    path('stripe/config/', stripe.config),
    path('stripe/create-checkout-session/', stripe.create_checkout_session, name='stripe_create_checkout_session'),
    path('stripe/webhook/', stripe.webhook),
]
