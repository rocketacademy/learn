import codecs
import csv
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render
from django.views import View

from payment.models import Coupon
from staff.forms.coupon import CouponForm
from staff.forms.coupon_generation import CouponGenerationForm


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

class CsvUploadView(LoginRequiredMixin, View):
    def get(self, request):
        coupon_generation_form = CouponGenerationForm(None)
        return render(
            request,
            'coupon/coupon_generation.html',
            {
                'coupon_generation_form': coupon_generation_form
            }
        )

    def post(self, request):
        form = CouponGenerationForm(request.POST, request.FILES)

        if not form.is_valid():
            return render(request, 'coupon/coupon_generation.html', {'coupon_generation_form': form})

        csv_file = form.cleaned_data.get('csv_file')
        csvreader = csv.DictReader(codecs.iterdecode(csv_file, 'utf-8'))
        csv_rows = []
        for row in csvreader:
            print('!! row in csv_file !!', row)
            csv_rows.append(row)

        return render(
            request,
            'coupon/coupon_generation_success.html',
            {
                'csv_rows': csv_rows
            }
        )
