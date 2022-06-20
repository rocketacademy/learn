from django.urls import path

from student.forms import BatchSelectionForm, StudentInfoForm
from student.views import index
from student.views import registration
from student.views import slack

FORMS = [
    ('batch_selection', BatchSelectionForm),
    ('student_info', StudentInfoForm)
]

urlpatterns = [
    path('', index.IndexView.as_view(), name='index'),
    path('basics/register/', registration.RegistrationWizard.as_view(FORMS), name='basics_register'),
    path('basics/register/<int:registration_id>/payment/',
         registration.PaymentPreviewView.as_view(),
         name='basics_register_payment_preview'),
    path('basics/register/<int:registration_id>/confirmation/',
         registration.ConfirmationView.as_view(),
         name='basics_register_confirmation'),
    path('slack/event/hook/', slack.event_hook, name='slack_event_hook')
]
