import csv
import os
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from staff.forms.csv_upload import CsvUploadForm

class TestCsvUploadForm:
    def test_empty_form_is_invalid(self):
        csv_upload_form = CsvUploadForm(data={})

        outcome = csv_upload_form.is_valid()

        assert outcome is False

    def test_file_uploaded_field_accepts_csv(self):
        file_path = "./staff/tests/forms/csv_files/correct_test_file.csv"

        csv_file = open(file_path, 'r')
        content = csv_file.read()
        csv_upload_form = CsvUploadForm(files={'csv_file': SimpleUploadedFile(name=csv_file.name, content=bytes(content, 'utf-8'), content_type="multipart/form-data")})

        assert csv_upload_form.is_valid()
        assert csv_upload_form.__dict__['files']['csv_file'].name.endswith('.csv')
