from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login_view'),
    path('coding-basics/batches/', views.batches_view, name='batches_view'),
    path('coding-basics/batches/<int:batch_id>/', views.batch_view, name='batch_view'),
    path('coding-basics/batches/<int:batch_id>/students/', views.students_view, name='students_view'),
    path('coding-basics/batches/<int:batch_id>/sections/', views.sections_view, name='sections_view'),
    path('coding-basics/batches/<int:batch_id>/sections/<int:section_id>/', views.section_view, name='section_view'),
    path('coding-basics/section-leaders/', views.section_leaders_view, name='section_leaders_view'),
]
