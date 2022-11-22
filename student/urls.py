from django.urls import path

from student.forms import BatchSelectionForm, StudentInfoForm
from student.views import certificate
from student.views import index
from student.views import registration
from student.views import slack

FORMS = [
    ('batch_selection', BatchSelectionForm),
    ('student_info', StudentInfoForm)
]

urlpatterns = [
    path('', index.IndexView.as_view(), name='index'),
    path('basics/certificates/<str:certificate_credential>/', certificate.DetailView.as_view(), name='basics_certificate'),
    path('slack/event/hook/', slack.event_hook, name='slack_event_hook'),
    path('courses/swe-fundamentals/register/', registration.RegistrationWizard.as_view(FORMS), name='swe_fundamentals_register'),
    path('courses/swe-fundamentals/register/<int:registration_id>/payment/',
         registration.PaymentPreviewView.as_view(),
         name='swe_fundamentals_register_payment_preview'),
    path('courses/swe-fundamentals/register/<int:registration_id>/confirmation/',
         registration.ConfirmationView.as_view(),
         name='swe_fundamentals_register_confirmation'),
]
