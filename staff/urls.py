from django.urls import path

from .views import coding_basics_view, index, login_view

urlpatterns = [
    path('', index, name='index'),
    path('login/', login_view, name='login_view'),
    path('coding_basics/', coding_basics_view, name='coding_basics_view')
]