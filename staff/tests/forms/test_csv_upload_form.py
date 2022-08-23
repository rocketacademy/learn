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
        file_path = "testfile.csv"
        file_content = [
            ['test1@test.com'],
            ['test2@test.com'],
        ]
        with open(file_path, 'w') as csv_file:
            writer = csv.writer(csv_file, dialect='excel')
            writer.writerows(file_content)

        csv_file = open(file_path, 'r')
        content = csv_file.read()
        csv_upload_form = CsvUploadForm(files={'csv_file': SimpleUploadedFile(name=csv_file.name, content=bytes(content, 'utf-8'), content_type="multipart/form-data")})
        os.remove(file_path)

        assert csv_upload_form.is_valid()
        assert csv_upload_form.__dict__['files']['csv_file'].name.endswith('.csv')
