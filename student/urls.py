from django.urls import path

from student.views import index
from student.views import basics

urlpatterns = [
    path('', index.IndexView.as_view(), name='index'),
    path('basics/register/', basics.RegistrationWizard.as_view(), name='basics_register'),
    path('basics/register/confirmation/', basics.ConfirmationView.as_view(), name='basics_register_confirmation')
]
