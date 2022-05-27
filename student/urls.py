from django.urls import path

from student.forms import BatchSelectionForm, StudentInfoForm
from student.views import index
from student.views import registration

FORMS = [
    ('batch_selection', BatchSelectionForm),
    ('student_info', StudentInfoForm)
]

urlpatterns = [
    path('', index.IndexView.as_view(), name='index'),
    path('basics/register/', registration.RegistrationWizard.as_view(FORMS), name='basics_register'),
    path(
        'basics/register/payment/<str:payable_type>/<int:payable_id>/',
        registration.PaymentPreviewView.as_view(),
        name='basics_register_payment_preview'
    ),
    path('basics/register/confirmation/', registration.ConfirmationView.as_view(), name='basics_register_confirmation')
]
