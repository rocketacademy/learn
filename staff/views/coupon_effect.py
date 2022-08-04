from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render
from django.views import View

from payment.models.coupon_effect import CouponEffect
from staff.forms.coupon_effect import CouponEffectForm
from staff.models import Course


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

    def post(self, request):
        coupon_effect_form = CouponEffectForm(request.POST)

        if coupon_effect_form.is_valid():
            try:
                with transaction.atomic():
                    coding_basics_course = Course.objects.get(name=settings.CODING_BASICS)
                    coupon_effect = coupon_effect_form.save()
                    coupon_effect.couponable_type = type(coding_basics_course).__name__
                    coupon_effect.couponable_id = coding_basics_course.id
                    coupon_effect.save()

                    return redirect('coupon_effect_detail', coupon_effect_id=coupon_effect.id)
            except IntegrityError:
                return redirect('coupon_effect_new')
        return render(
            request,
            'coupon_effect/new.html',
            {
                'coupon_effect_form': coupon_effect_form
            }
        )

class DetailView(LoginRequiredMixin, View):
    def get(self, request, coupon_effect_id):
        coupon_effect = CouponEffect.objects.get(pk=coupon_effect_id)

        return render(
            request,
            'coupon_effect/detail.html',
            {
                'coupon_effect': coupon_effect,
            }
        )
