from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render
from django.views import View

from payment.models.coupon_effect import CouponEffect
from staff.forms.coupon_effect import CouponEffectForm


class NewView(LoginRequiredMixin, View):
    def get(self, request):
        coupon_effect_form = CouponEffectForm(None)

        return render(
            request,
            'coupon_effect/new.html',
            {
                'coupon_effect_form': coupon_effect_form
            }
        )

    # def post(self, request):
    #     coupon_form = CouponForm(request.POST)

    #     if coupon_form.is_valid():
    #         try:
    #             with transaction.atomic():
    #                 coupon = coupon_form.save()

    #                 return redirect('coupon_detail', coupon_id=coupon.id)
    #         except IntegrityError:
    #             return redirect('coupon_new')
    #     return render(
    #         request,
    #         'coupon/new.html',
    #         {
    #             'coupon_form': coupon_form
    #         }
    #     )