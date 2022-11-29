from django.urls import path

from staff.views import batch, coupon, coupon_effect, index, login
from staff.views.course.swe_fundamentals import basics_batch, basics_enrolment, basics_registration, basics_section
from staff.views.course.bootcamp import bootcamp_batch

urlpatterns = [
    path('', index.IndexView.as_view(), name='staff_index'),
    path('basics/batches/<int:batch_id>/graduate/', basics_batch.GraduateView.as_view(), name='basics_batch_graduate'),
    path('batches/', batch.ListView.as_view(), name='batch_list'),
    path('batches/<int:batch_id>/', batch.DetailView.as_view(), name='batch_detail'),
    path('coupons/', coupon.ListView.as_view(), name='coupon_list'),
    path('coupons/new/', coupon.NewView.as_view(), name='coupon_new'),
    path('coupons/new/batch/', coupon.NewBatchView.as_view(), name='coupon_new_batch'),
    path('coupons/<int:coupon_id>/', coupon.DetailView.as_view(), name='coupon_detail'),
    path('coupons/<int:coupon_id>/edit/', coupon.EditView.as_view(), name='coupon_edit'),
    path('coupon-effects/new/', coupon_effect.NewView.as_view(), name='coupon_effect_new'),
    path('coupon-effects/<int:coupon_effect_id>/', coupon_effect.DetailView.as_view(), name='coupon_effect_detail'),
    path('courses/bootcamp/batches/', bootcamp_batch.ListView.as_view(), name='bootcamp_batch_list'),
    path('courses/bootcamp/batches/new/', bootcamp_batch.NewView.as_view(), name='bootcamp_batch_new'),
    path('courses/bootcamp/batches/<int:batch_id>/', bootcamp_batch.DetailView.as_view(), name='bootcamp_batch_detail'),
    path('courses/bootcamp/batches/<int:batch_id>/edit/', bootcamp_batch.EditView.as_view(), name='bootcamp_batch_edit'),
    path('courses/swe-fundamentals/batches/', basics_batch.ListView.as_view(), name='swe_fundamentals_batch_list'),
    path('courses/swe-fundamentals/batches/new/', basics_batch.NewView.as_view(), name='swe_fundamentals_batch_new'),
    path('courses/swe-fundamentals/batches/<int:batch_id>/', basics_batch.DetailView.as_view(), name='swe_fundamentals_batch_detail'),
    path('courses/swe-fundamentals/batches/<int:batch_id>/edit/', basics_batch.EditView.as_view(), name='swe_fundamentals_batch_edit'),
    path(
        'courses/swe-fundamentals/batches/<int:batch_id>/enrolments/',
        basics_enrolment.ListView.as_view(),
        name='swe_fundamentals_batch_enrolment_list'
    ),
    path(
        'courses/swe-fundamentals/batches/<int:batch_id>/enrolments/create-zoom-breakout-csv/',
        basics_enrolment.create_zoom_breakout_csv,
        name='swe_fundamentals_batch_create_zoom_breakout_csv'
    ),
    path(
        'courses/swe-fundamentals/batches/<int:batch_id>/registrations/',
        basics_registration.ListView.as_view(),
        name='swe_fundamentals_batch_registration_list'
    ),
    path(
        'courses/swe-fundamentals/batches/<int:batch_id>/sections/',
        basics_section.ListView.as_view(),
        name='swe_fundamentals_batch_section_list'
    ),
    path(
        'courses/swe-fundamentals/batches/<int:batch_id>/sections/<int:section_id>/',
        basics_section.DetailView.as_view(),
        name='swe_fundamentals_batch_section_detail'
    ),
    path('login/', login.LoginView.as_view(), name='staff_login'),
]
