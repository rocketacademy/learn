from django import forms
from django.core.exceptions import ValidationError

from payment.models.coupon import Coupon

class CsvUploadForm(forms.Form):
    csv_file = forms.FileField()
