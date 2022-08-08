from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render
from django.views import View
import stripe

from payment.library.stripe import Stripe
from payment.models.coupon_effect import CouponEffect
from staff.forms.stripe_coupon_effect import StripeCouponEffectForm
from staff.models import Course


class NewView(LoginRequiredMixin, View):
    def get(self, request):
        stripe_coupon_effect_form = StripeCouponEffectForm(None)

        return render(
            request,
            'coupon_effect/new.html',
            {
                'stripe_coupon_effect_form': stripe_coupon_effect_form
            }
        )

    def post(self, request):
        stripe_coupon_effect_form = StripeCouponEffectForm(request.POST)

        if stripe_coupon_effect_form.is_valid():
            try:
                with transaction.atomic():
                    stripe_coupon_effect = stripe_coupon_effect_form.save()
                    coding_basics_course = Course.objects.get(name=settings.CODING_BASICS)
                    discount = {
                        'type': stripe_coupon_effect.discount_type,
                        'amount': stripe_coupon_effect.discount_amount
                    }

                    stripe_coupon = Stripe().create_coupon(discount)
                    print(stripe_coupon)
                    stripe_coupon_effect.couponable_type = type(coding_basics_course).__name__
                    stripe_coupon_effect.couponable_id = coding_basics_course.id
                    stripe_coupon_effect.stripe_coupon_id = stripe_coupon['id']
                    stripe_coupon_effect.save()

                    return redirect('coupon_effect_detail', coupon_effect_id=stripe_coupon_effect.id)
            except IntegrityError:
                return redirect('coupon_effect_new')
        return render(
            request,
            'coupon_effect/new.html',
            {
                'stripe_coupon_effect_form': stripe_coupon_effect_form
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
