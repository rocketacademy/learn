import datetime
from django import forms

from staff.models import Batch

class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = [
            'start_date',
            'end_date',
            'sections'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'sections': forms.NumberInput()
        }

    def clean(self):
        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')

        if start_date and end_date and start_date >= end_date:
            message = forms.ValidationError(('Start date must be before end date'), code='invalid_date')
            self.add_error('start_date', message)
            self.add_error('end_date', message)

        return self.cleaned_data

    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')

        if start_date < datetime.date.today():
            raise forms.ValidationError(
                ('Start date should be in the future'),
                code='invalid_start_date'
            )

        return start_date

    def clean_sections(self):
        sections = self.cleaned_data.get('sections')

        if not sections > 0:
            raise forms.ValidationError(
                ('Each batch should have at least one section'),
                code='no_sections',
            )

        return sections
