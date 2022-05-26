from django import forms
from django.utils.html import format_html

from staff.models import Batch
from student.models.registration import Registration

class BatchChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%i" % obj.number

class BatchSelectionForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = [
            'batch',
        ]
        widgets = {
            'batch': forms.RadioSelect()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['batch'].label_from_instance = lambda item: format_html(
            "<h6>{} - {} to {}</h6>{}",
            item,
            item.start_date.strftime("%d %B"),
            item.end_date.strftime("%d %B"),
            Batch.html_formatted_batch_schedules(item)
        )

    def clean(self):
        batch = self.cleaned_data.get('batch')

        if batch is None:
            raise forms.ValidationError(
                ('Please select a batch'),
                code='invalid_batch_selection'
            )

        return self.cleaned_data
