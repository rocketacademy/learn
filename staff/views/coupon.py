import codecs
import csv
import datetime
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.shortcuts import redirect, render
from django.utils.timezone import make_aware
from django.views import View
from sendgrid.helpers.mail import CustomArg, Email, Personalization

from emails.library.sendgrid import Sendgrid
from payment.models import Coupon
from payment.models.coupon_effect import CouponEffect
from staff.forms.coupon import CouponForm
from staff.forms.coupon_batch import CouponBatchForm
from staff.models import Course


class ListView(LoginRequiredMixin, View):
    def get(self, request):
        coupon_queryset = Coupon.objects.all().order_by('-created_at')
        query = request.GET.get('query')

        if query:
            coupon_queryset = Coupon.objects.filter(
                Q(description__icontains=query) | Q(code__icontains=query)
            ).distinct()

        coupon_paginator = Paginator(coupon_queryset, 15)
        page_number = request.GET.get('page')
        coupon_page_obj = coupon_paginator.get_page(page_number)

        return render(
            request,
            'coupon/list.html',
            {
                'coupon_page_obj': coupon_page_obj
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
        code = request.POST['code']

        if Coupon.objects.filter(code=code).exists():
            coupon_form.add_error(
                'code',
                f"Coupon with code {code} already exists"
            )

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

class EditView(LoginRequiredMixin, View):
    def get(self, request, coupon_id):
        coupon = Coupon.objects.get(pk=coupon_id)
        coupon_form = CouponForm(instance=coupon)

        return render(
            request,
            'coupon/edit.html',
            {
                'coupon': coupon,
                'coupon_effects': coupon.effects.all(),
                'coupon_form': coupon_form
            }
        )

    def post(self, request, coupon_id):
        coupon = Coupon.objects.get(pk=coupon_id)
        coupon_form = CouponForm(request.POST)

        if coupon_form.is_valid():
            try:
                with transaction.atomic():
                    coupon.start_date = coupon_form.cleaned_data.get('start_date')
                    coupon.end_date = coupon_form.cleaned_data.get('end_date')
                    coupon.description = coupon_form.cleaned_data.get('description')
                    coupon_effects = []
                    for effect in coupon_form.cleaned_data.get('effects'):
                        coupon_effects.append(effect)
                    coupon.effects.set(coupon_effects)
                    coupon.save()

                    return redirect('coupon_detail', coupon_id=coupon.id)
            except IntegrityError:
                return redirect('coupon_edit', coupon_id=coupon.id)

        return render(
            request,
            'coupon/edit.html',
            {
                'coupon': coupon,
                'coupon_effects': coupon.effects.all(),
                'coupon_form': coupon_form,
            }
        )

class NewBatchView(LoginRequiredMixin, View):
    def get(self, request):
        form = CouponBatchForm(None)
        return render(
            request,
            'coupon/new_batch.html',
            {
                'coupon_batch_form': form
            }
        )

    def post(self, request):
        form = CouponBatchForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(request, 'coupon/new_batch.html', {'coupon_batch_form': form})

        csv_file = form.cleaned_data.get('csv_file')
        csvreader = csv.DictReader(codecs.iterdecode(csv_file, 'utf-8'))
        coding_basics_course = Course.objects.get(name=Course.CODING_BASICS)
        coding_basics_coupon_effect = CouponEffect.objects.get(
            couponable_type=type(coding_basics_course).__name__,
            couponable_id=coding_basics_course.id,
            discount_type=CouponEffect.DOLLARS,
            discount_amount=20
        )
        coding_bootcamp_course = Course.objects.get(name=Course.CODING_BOOTCAMP)
        coding_bootcamp_coupon_effect = CouponEffect.objects.get(
            couponable_type=type(coding_bootcamp_course).__name__,
            couponable_id=coding_bootcamp_course.id,
            discount_type=CouponEffect.DOLLARS,
            discount_amount=200
        )
        personalizations = []

        for row in csvreader:
            to_email = row['email']
            first_name = row['first_name']

            coupon = Coupon.objects.create(
                start_date=make_aware(datetime.datetime.now()),
                end_date=None,
                description=to_email
            )
            coupon.effects.set([coding_basics_coupon_effect, coding_bootcamp_coupon_effect])
            coupon.save()

            personalization = Personalization()
            personalization.add_to(Email(to_email))
            personalization.add_custom_arg(CustomArg('emailable_type', type(coupon).__name__))
            personalization.add_custom_arg(CustomArg('emailable_id', coupon.id))
            personalization.dynamic_template_data = {
                'first_name': first_name.capitalize(),
                'referral_code': coupon.code,
            }
            personalizations.append(personalization)
        sendgrid_client = Sendgrid()
        sendgrid_client.send_bulk(
            settings.ROCKET_COMMUNITY_EMAIL,
            personalizations,
            settings.COUPON_CODE_NOTIFICATION_TEMPLATE_ID
        )
        return redirect('coupon_list')
