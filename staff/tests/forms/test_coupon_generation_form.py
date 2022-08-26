import csv
import os
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from staff.forms.coupon_generation import CouponBatchForm

class TestCouponBatchForm:
    def test_empty_form_is_invalid(self):
        coupon_batch_form = CouponBatchForm(data={})

        outcome = coupon_batch_form.is_valid()

        assert outcome is False

    def test_file_upload_field_validates_for_only_csv_extension(self):
        coupon_batch_form = CouponBatchForm(
            files={
                'csv_file': SimpleUploadedFile(
                    name="wrongname.cs",
                    content=bytes('test content', 'utf-8'),
                    content_type="multipart/form-data"
                )
            }
        )

        outcome = coupon_batch_form.is_valid()

        assert outcome is False
        assert "The file you uploaded is not a .csv file!" in coupon_batch_form.errors['csv_file']
