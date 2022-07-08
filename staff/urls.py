from django.urls import path

from staff.views import coupon, batch, index, login, section, student

urlpatterns = [
    path('', index.IndexView.as_view(), name='index'),
    path('basics/batches/', batch.ListView.as_view(), name='batch_list'),
    path('basics/batches/new/', batch.NewView.as_view(), name='batch_new'),
    path('basics/batches/<int:batch_id>/', batch.DetailView.as_view(), name='batch_detail'),
    path('basics/batches/<int:batch_id>/edit/', batch.EditView.as_view(), name='batch_edit'),
    path('basics/batches/<int:batch_id>/students/', student.ListView.as_view(), name='student_list'),
    path('basics/batches/<int:batch_id>/sections/', section.ListView.as_view(), name='section_list'),
    path('basics/batches/<int:batch_id>/sections/<int:section_id>/', section.DetailView.as_view(), name='section_detail'),
    path('coupons/', coupon.ListView.as_view(), name='coupon_list'),
    path('coupons/new/', coupon.NewView.as_view(), name='coupon_new'),
    path('login/', login.LoginView.as_view(), name='staff_login'),
]
