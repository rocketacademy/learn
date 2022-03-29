from django.urls import path

from .views import coding_basics, index, login_view

urlpatterns = [
    path('', index, name='index'),
    path('login/', login_view, name='login_view'),
    path('coding_basics/', coding_basics, name='coding_basics')
]