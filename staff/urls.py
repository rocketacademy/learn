from django.urls import path

from .views import batch_overview_view, batch_sections_view, batch_students_view, coding_basics_view, index, login_view, admin_batches_view, admin_section_leaders_view

urlpatterns = [
    path('', index, name='index'),
    path('login/', login_view, name='login_view'),
    path('coding_basics/', coding_basics_view, name='coding_basics_view'),
    # To-do: Update the following URLs when BatchViewSet is ready
    path('batch/overview', batch_overview_view, name='batch_overview_view'),
    path('batch/students', batch_students_view, name='batch_students_view'),
    path('batch/sections', batch_sections_view, name='batch_sections_view'),
    path('coding_basics/admin/batches', admin_batches_view, name="admin_batches_view"),
    path('coding_basics/admin/section-leaders.html', admin_section_leaders_view, name="admin_section_leaders_view")
]