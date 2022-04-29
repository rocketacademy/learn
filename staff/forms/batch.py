import datetime
from django import forms


class BatchForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    sections = forms.IntegerField(widget=forms.NumberInput(), label='No. of sections')
    section_capacity = forms.IntegerField(widget=forms.NumberInput())

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

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

    def clean_section_capacity(self):
        section_capacity = self.cleaned_data.get('section_capacity')

        if not section_capacity > 0:
            raise forms.ValidationError(
                ('Capacity per section should be more than one'),
                code='invalid_section_capacity',
            )

        return section_capacity
