from django.urls import path

from emails.views import sendgrid


urlpatterns = [
    path('sendgrid/event-webhook/', sendgrid.event_webhook)
]
