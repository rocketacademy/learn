from django.urls import path
from payment import views

urlpatterns = [
    path('config/', views.stripe_config),
    path('create-checkout-session/<str:payable_type>/<int:payable_id>/', views.create_checkout_session, name='create_checkout_session'),
    path('webhook/', views.stripe_webhook),
]
