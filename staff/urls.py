from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login_view'),
    path('coding-basics/batches/', views.batch_list, name='batch_list'),
    path('coding-basics/batches/<int:batch_id>/', views.batch_detail, name='batch_detail'),
    path('coding-basics/batches/<int:batch_id>/students/', views.student_list, name='student_list'),
    path('coding-basics/batches/<int:batch_id>/sections/', views.section_list, name='section_list'),
    path('coding-basics/batches/<int:batch_id>/sections/<int:section_id>/', views.section_detail, name='section_detail'),
    path('coding-basics/section-leaders/', views.section_leader_list, name='section_leader_list'),
]
