from django.urls import path

from student.views import registration

urlpatterns = [
    path('registration/batch-selection/',
         registration.select_batch, name='select_batch'),
]
