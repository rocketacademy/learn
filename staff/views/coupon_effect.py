from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render
from django.views import View
import stripe

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
                    coding_basics_course = Course.objects.get(name=settings.CODING_BASICS)
                    stripe_coupon_effect = stripe_coupon_effect_form.save()
                    stripe_coupon_effect.couponable_type = type(coding_basics_course).__name__
                    stripe_coupon_effect.couponable_id = coding_basics_course.id
                    discount = {
                        'type': stripe_coupon_effect.discount_type,
                        'amount': stripe_coupon_effect.discount_amount * 100
                    }
                    stripe_coupon = create_stripe_coupon(discount)
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

def create_stripe_coupon(discount):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    if discount['type'] == 'percent':
        stripe_coupon = stripe.Coupon.create(
            percent_off=discount['amount'],
            duration='forever'
        )
    elif discount['type'] == 'dollars':
        stripe_coupon = stripe.Coupon.create(
            amount_off=discount['amount'],
            duration='forever',
            currency=settings.SINGAPORE_DOLLAR_CURRENCY
        )

    return stripe_coupon
