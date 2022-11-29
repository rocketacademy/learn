from django.urls import path

from staff.views import batch, coupon, coupon_effect, index, login
from staff.views.basics import basics_batch, basics_enrolment, basics_registration, basics_section
from staff.views.bootcamp import bootcamp_batch

urlpatterns = [
    path('', index.IndexView.as_view(), name='staff_index'),
    path('swe-fundamentals/batches/', basics_batch.ListView.as_view(), name='swe_fundamentals_batch_list'),
    path('swe-fundamentals/batches/new/', basics_batch.NewView.as_view(), name='swe_fundamentals_batch_new'),
    path('basics/batches/<int:batch_id>/', basics_batch.DetailView.as_view(), name='basics_batch_detail'),
    path('basics/batches/<int:batch_id>/edit/', basics_batch.EditView.as_view(), name='basics_batch_edit'),
    path('basics/batches/<int:batch_id>/enrolments/', basics_enrolment.ListView.as_view(), name='basics_batch_enrolment_list'),
    path(
        'basics/batches/<int:batch_id>/enrolments/create-zoom-breakout-csv/',
        basics_enrolment.create_zoom_breakout_csv,
        name='basics_batch_create_zoom_breakout_csv'
    ),
    path('basics/batches/<int:batch_id>/graduate/', basics_batch.GraduateView.as_view(), name='basics_batch_graduate'),
    path('basics/batches/<int:batch_id>/registrations/', basics_registration.ListView.as_view(), name='basics_batch_registration_list'),
    path('basics/batches/<int:batch_id>/sections/', basics_section.ListView.as_view(), name='basics_batch_section_list'),
    path('basics/batches/<int:batch_id>/sections/<int:section_id>/', basics_section.DetailView.as_view(), name='basics_batch_section_detail'),
    path('bootcamp/batches/', bootcamp_batch.ListView.as_view(), name='bootcamp_batch_list'),
    path('bootcamp/batches/new/', bootcamp_batch.NewView.as_view(), name='bootcamp_batch_new'),
    path('bootcamp/batches/<int:batch_id>/', bootcamp_batch.DetailView.as_view(), name='bootcamp_batch_detail'),
    path('bootcamp/batches/<int:batch_id>/edit/', bootcamp_batch.EditView.as_view(), name='bootcamp_batch_edit'),
    path('coupons/', coupon.ListView.as_view(), name='coupon_list'),
    path('coupons/new/', coupon.NewView.as_view(), name='coupon_new'),
    path('coupons/new/batch/', coupon.NewBatchView.as_view(), name='coupon_new_batch'),
    path('coupons/<int:coupon_id>/', coupon.DetailView.as_view(), name='coupon_detail'),
    path('coupons/<int:coupon_id>/edit/', coupon.EditView.as_view(), name='coupon_edit'),
    path('coupon-effects/new/', coupon_effect.NewView.as_view(), name='coupon_effect_new'),
    path('coupon-effects/<int:coupon_effect_id>/', coupon_effect.DetailView.as_view(), name='coupon_effect_detail'),
    path('courses/batches/', batch.ListView.as_view(), name='batch_list'),
    path('courses/batches/<int:batch_id>/', batch.DetailView.as_view(), name='batch_detail'),
    path('login/', login.LoginView.as_view(), name='staff_login'),
]
