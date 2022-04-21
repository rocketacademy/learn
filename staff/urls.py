from django.urls import path
from .views import batch_view, sections_view, section_view, students_view, index, login_view, batches_view, section_leaders_view

urlpatterns = [
    path('', index, name='index'),
    path('login/', login_view, name='login_view'),
    path('coding-basics/batches/', batches_view, name='batches_view'),
    path('coding-basics/batches/<int:batch_id>/', batch_view, name='batch_view'),
    path('coding-basics/batches/<int:batch_id>/students/', students_view, name='students_view'),
    path('coding-basics/batches/<int:batch_id>/sections/', sections_view, name='sections_view'),
    path('coding-basics/batches/<int:batch_id>/sections/<int:section_id>/', section_view, name='section_view'),
    path('coding-basics/section-leaders/', section_leaders_view, name='section_leaders_view'),
]