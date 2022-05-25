from django.urls import path

from student.forms.registration.basics import BatchSelectionForm, StudentInfoForm
from student.views import index
from student.views import registration

FORMS = [
    ('batch_selection', BatchSelectionForm),
    ('student_info', StudentInfoForm)
]

urlpatterns = [
    path('', index.IndexView.as_view(), name='index'),
    path('basics/register/', registration.RegistrationWizard.as_view(FORMS), name='basics_register'),
    path('basics/register/confirmation/', registration.ConfirmationView.as_view(), name='basics_register_confirmation')
]
