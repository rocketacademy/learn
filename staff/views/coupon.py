from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render
from django.views import View

from payment.models import Coupon
from staff.forms.coupon import CouponForm


class ListView(LoginRequiredMixin, View):
    def get(self, request):
        coupon_queryset = Coupon.objects.all().order_by('-created_at')

        return render(
            request,
            'coupon/list.html',
            {
                'coupons': coupon_queryset
            }
        )

class NewView(LoginRequiredMixin, View):
    def get(self, request):
        coupon_form = CouponForm(None)

        return render(
            request,
            'coupon/new.html',
            {
                'coupon_form': coupon_form
            }
        )

    def post(self, request):
        coupon_form = CouponForm(request.POST)

        if coupon_form.is_valid():
            try:
                with transaction.atomic():
                    coupon = coupon_form.save()

                    return redirect('coupon_detail', coupon_id=coupon.id)
            except IntegrityError:
                return redirect('coupon_new')
        return render(
            request,
            'coupon/new.html',
            {
                'coupon_form': coupon_form
            }
        )

class DetailView(LoginRequiredMixin, View):
    def get(self, request, coupon_id):
        coupon = Coupon.objects.get(pk=coupon_id)

        return render(
            request,
            'coupon/detail.html',
            {
                'coupon': coupon,
                'coupon_effects': coupon.effects.all()
            }
        )
