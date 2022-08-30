import codecs
import csv
from django import forms

class CouponBatchForm(forms.Form):
    csv_file = forms.FileField()

    def clean_csv_file(self):
        csv_file = self.cleaned_data.get('csv_file')

        if not csv_file.name.endswith('.csv'):
            self.add_error(
                'csv_file',
                'The file you uploaded is not a .csv file!'
            )
            return self.cleaned_data

        csvreader = csv.DictReader(codecs.iterdecode(csv_file, 'utf-8'))
        for row in csvreader:
            if not len(list(row)) == 2:
                self.add_error(
                    'csv_file',
                    'The uploaded csv file requires TWO specific headers "first_name" and "email".'
                )
                return self.cleaned_data
            if not list(row) == ['first_name', 'email']:
                self.add_error(
                    'csv_file',
                    'The file you uploaded requires the specific headers "first_name" and "email"!'
                )
                return self.cleaned_data
        return self.cleaned_data['csv_file']
