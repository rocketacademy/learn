from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render
from django.views import View

from payment.models.coupon_effect import CouponEffect
from staff.forms.coupon_effect import CouponEffectForm
from staff.forms.course import CourseForm
from staff.models import Course


class NewView(LoginRequiredMixin, View):
    def get(self, request):
        course_form = CourseForm(None)
        coupon_effect_form = CouponEffectForm(None)

        return render(
            request,
            'coupon_effect/new.html',
            {
                'course_form': course_form,
                'coupon_effect_form': coupon_effect_form
            }
        )

    def post(self, request):
        course_form = CourseForm(request.POST)
        coupon_effect_form = CouponEffectForm(request.POST)

        if course_form.is_valid() and coupon_effect_form.is_valid():
            try:
                with transaction.atomic():
                    couponable = Course.objects.get(name=course_form.cleaned_data['name'])
                    coupon_effect = CouponEffect()

                    coupon_effect.couponable_type = type(couponable).__name__
                    coupon_effect.couponable_id = couponable.id
                    coupon_effect.discount_type = coupon_effect_form.cleaned_data['discount_type']
                    coupon_effect.discount_amount = coupon_effect_form.cleaned_data['discount_amount']
                    coupon_effect.save()

                    return redirect('coupon_effect_detail', coupon_effect_id=coupon_effect.id)
            except IntegrityError:
                return redirect('coupon_effect_new')
        return render(
            request,
            'coupon_effect/new.html',
            {
                'course_form': course_form,
                'coupon_effect_form': coupon_effect_form
            }
        )

class DetailView(LoginRequiredMixin, View):
    def get(self, request, coupon_effect_id):
        coupon_effect = CouponEffect.objects.get(pk=coupon_effect_id)
        couponable = apps.get_model('staff', coupon_effect.couponable_type).objects.get(pk=coupon_effect.couponable_id)

        return render(
            request,
            'coupon_effect/detail.html',
            {
                'couponable': couponable,
                'coupon_effect': coupon_effect,
            }
        )
