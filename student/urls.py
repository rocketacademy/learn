from django.urls import path

from student.views import registration

urlpatterns = [
    path('registration/student-registration/',
         registration.StudentRegistrationView.as_view(), name='student_registration'),
    path('registration/confirmation/',
         registration.ConfirmationView.as_view(), name='confirmation')
]
