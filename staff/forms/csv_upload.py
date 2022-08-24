from django import forms
from django.core.exceptions import ValidationError

class CsvUploadForm(forms.Form):
    csv_file = forms.FileField()

    def clean(self):
        csv_file = self.cleaned_data.get('csv_file')

        if csv_file is None:
            self.add_error(
                'csv_file',
                'Please ensure you uploaded a .csv file!'
            )
            return self

        if not csv_file.name.endswith('.csv'):
            self.add_error(
                'csv_file',
                'The file you uploaded is not a .csv file!'
            )
            return self.cleaned_data

        for index, row in enumerate(csv_file):
            row_data = str(row.decode('utf-8')).split(",")
            first_name = row_data[0]
            # replace to remove csv formatting for new row
            email = row_data[1].replace('\\r\\n', '')
            if index == 0:
                if "first_name" not in first_name and "email" not in email:
                    self.add_error(
                        'csv_file',
                        'The file you uploaded requires the headers "first_name" and "email!'
                    )
                    return self.cleaned_data

        return self.cleaned_data
