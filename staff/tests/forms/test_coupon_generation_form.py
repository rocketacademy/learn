import csv
import os
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from staff.forms.coupon_generation import CouponGenerationForm

class TestCouponGenerationForm:
    def test_empty_form_is_invalid(self):
        coupon_generation_form = CouponGenerationForm(data={})

        outcome = coupon_generation_form.is_valid()

        assert outcome is False

    def test_file_uploaded_field_accepts_csv(self):
        coupon_generation_form = CouponGenerationForm(
            files={
                'csv_file': SimpleUploadedFile(
                    name="wrongname.cs",
                    content=bytes('test content', 'utf-8'),
                    content_type="multipart/form-data"
                )
            }
        )

        outcome = coupon_generation_form.is_valid()

        assert outcome is False
        assert not coupon_generation_form.__dict__['files']['csv_file'].name.endswith('.csv')
