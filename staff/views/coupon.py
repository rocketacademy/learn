from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render
from django.views import View

from payment.models import Coupon
from staff.forms.coupon import CouponForm
from staff.forms.csv_upload import CsvUploadForm


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
        csv_upload_form = CsvUploadForm(None)
        return render(
            request,
            'coupon/csv_upload.html',
            {
                'csv_upload_form': csv_upload_form
            }
        )

    def post(self, request):
        form = CsvUploadForm(request.POST, request.FILES)

        if not form.is_valid():
            return render(request, 'coupon/csv_upload.html', {'csv_upload_form': form})
        csv_file = form.cleaned_data.get('csv_file')

        for row in csv_file:
            row_data = str(row.decode('utf-8')).split(",")
            first_name = row_data[0]
            # replace to remove csv formatting for new row
            email = row_data[1].replace('\\r\\n', '')
            
        return redirect('coupon_csv_upload')
