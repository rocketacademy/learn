# import datetime
from django import forms
from ..models import Batch
# from crispy_forms.helper import FormHelper
# from crispy_forms.layout import Layout, Submit, Row, Column


class CreateBatchForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Batch
        fields = ['course', 'start_date', 'end_date', 'sections', 'capacity']
        widgets = {
            'course': forms.TextInput(attrs={'type': 'hidden', 'value': 'CODING_BASICS'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    # def clean_start_date(self):
    #     start_date = self.cleaned_data.get('start_date')
    #     print('start date', start_date)
    #     print('string start date', str(start_date))

    #     formatted_start_date = datetime.datetime.strptime(str(start_date), "%Y-%m-%d").date()
    #     today = datetime.date.today()

    #     if formatted_start_date > today:
    #         raise forms.ValidationError('Start date cannot be before current date')

    # def check_start_end_dates(self):
    #     print('cleaned data', self.cleaned_data)
    #     end_date = self.cleaned_data.get('end_date')
    #     formatted_end_date = datetime.datetime.strptime(str(end_date), "%Y-%m-%d").date()

    #     start_date = self.cleaned_data.get('start_date')
    #     print('start date', start_date)

    #     formatted_start_date = datetime.datetime.strptime(str(start_date), "%Y-%m-%d").date()

    #     if formatted_start_date > formatted_end_date:
    #         raise forms.ValidationError(
    #             'Start date cannot be after end date'
    #         )

    #     return end_date
