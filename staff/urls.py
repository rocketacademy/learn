from django.urls import path

from staff.views import batch, index, login, section, student

urlpatterns = [
    path('', index.index, name='index'),
    path('login/', login.staff_login, name='staff_login'),
    path('basics/batches/', batch.batch_list, name='batch_list'),
    path('basics/batches/new/', batch.batch_new, name='batch_new'),
    path('basics/batches/<int:batch_id>/', batch.batch_detail, name='batch_detail'),
    path('basics/batches/<int:batch_id>/students/', student.student_list, name='student_list'),
    path('basics/batches/<int:batch_id>/sections/', section.section_list, name='section_list'),
    path('basics/batches/<int:batch_id>/sections/<int:section_id>/', section.section_detail, name='section_detail'),
]
