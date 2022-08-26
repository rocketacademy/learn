from django.urls import path

from staff.views import batch, coupon, coupon_effect, enrolment, index, login, section

urlpatterns = [
    path('', index.IndexView.as_view(), name='index'),
    path('basics/batches/', batch.ListView.as_view(), name='batch_list'),
    path('basics/batches/new/', batch.NewView.as_view(), name='batch_new'),
    path('basics/batches/<int:batch_id>/', batch.DetailView.as_view(), name='batch_detail'),
    path('basics/batches/<int:batch_id>/edit/', batch.EditView.as_view(), name='batch_edit'),
    path('basics/batches/<int:batch_id>/enrolments/', enrolment.ListView.as_view(), name='enrolment_list'),
    path(
        'basics/batches/<int:batch_id>/enrolments/create-zoom-breakout-csv/',
        enrolment.create_zoom_breakout_csv,
        name='create_zoom_breakout_csv'
    ),
    path('basics/batches/<int:batch_id>/sections/', section.ListView.as_view(), name='section_list'),
    path('basics/batches/<int:batch_id>/sections/<int:section_id>/', section.DetailView.as_view(), name='section_detail'),
    path('coupons/', coupon.ListView.as_view(), name='coupon_list'),
    path('coupons/new/batch/', coupon.NewBatchView.as_view(), name='coupon_new_batch'),
    path('coupons/new/', coupon.NewView.as_view(), name='coupon_new'),
    path('coupons/<int:coupon_id>/', coupon.DetailView.as_view(), name='coupon_detail'),
    path('coupons/<int:coupon_id>/edit/', coupon.EditView.as_view(), name='coupon_edit'),
    path('coupon-effects/new/', coupon_effect.NewView.as_view(), name='coupon_effect_new'),
    path('coupon-effects/<int:coupon_effect_id>/', coupon_effect.DetailView.as_view(), name='coupon_effect_detail'),
    path('login/', login.LoginView.as_view(), name='staff_login'),
]
