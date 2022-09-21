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
from sendgrid.helpers.mail import Mail

from emails.library.sendgrid import Sendgrid
from payment.models import Coupon
from payment.models.coupon_effect import CouponEffect
from staff.forms.coupon import CouponForm
from staff.forms.coupon_batch import CouponBatchForm
from staff.models import Course


class ListView(LoginRequiredMixin, View):
    def get(self, request):
        coupon_queryset = Coupon.objects.all().order_by('-created_at')
        query = request.GET.get('q')

        if query:
            coupon_queryset = Coupon.objects.filter(
                Q(description__icontains=query) | Q(code__icontains=query)
            ).distinct()

        coupon_paginator = Paginator(coupon_queryset, 2)
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
        course_basics = Course.objects.get(name=settings.CODING_BASICS)
        course_bootcamp = Course.objects.get(name=settings.CODING_BOOTCAMP)
        coupon_effect_basics = CouponEffect.objects.filter(
            couponable_id=course_basics.id,
            discount_type='dollars',
            discount_amount='20'
        ).first()
        coupon_effect_bootcamp = CouponEffect.objects.filter(
            couponable_id=course_bootcamp.id,
            discount_type='dollars',
            discount_amount='200'
        ).first()

        from_email = settings.ROCKET_COMMUNITY_EMAIL
        template_id = settings.COUPON_CODE_NOTIFICATION_TEMPLATE_ID

        for row in csvreader:
            coupon = Coupon.objects.create(
                start_date=make_aware(datetime.datetime.now()),
                end_date=None,
                description=row['email']
            )
            coupon.effects.set([coupon_effect_basics, coupon_effect_bootcamp])
            coupon.save()

            to_email = row['email']
            message = Mail(
                from_email=from_email,
                to_emails=to_email,
            )
            message.dynamic_template_data = {
                'first_name': row['first_name'],
                'referral_code': coupon.code,
            }
            message.template_id = template_id

            sendgrid_client = Sendgrid()
            sendgrid_client.send(
                coupon.id,
                type(coupon).__name__,
                from_email,
                to_email,
                template_id,
                message
            )

        return redirect('coupon_list')
