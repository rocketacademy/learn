from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View

from payment.models import Coupon

class ListView(LoginRequiredMixin, View):
    def get(self, request):
        coupon_queryset = Coupon.objects.all()

        return render(
            request,
            'coupon/list.html',
            {
                'coupons': coupon_queryset
            }
        )

class NewView(LoginRequiredMixin, View):
    def get(self, request):
        return render(
            request,
            'coupon/new.html',
        )
