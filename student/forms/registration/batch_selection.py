import datetime
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
        active_batches = Batch.swe_fundamentals_objects.filter(start_date__gte=datetime.date.today())
        # Kai: 9 is the batch ID for Fundamentals 21. Hard-coding this to hard-close F21 signups early.
        enrollable_batches_ids = [batch.id for batch in active_batches if not batch.fully_enrolled(), 9]
        enrollable_batches = Batch.swe_fundamentals_objects.filter(id__in=enrollable_batches_ids).order_by('start_date')

        self.fields['batch'].queryset = enrollable_batches
        self.fields['batch'].initial = enrollable_batches.first()
        self.fields['batch'].label_from_instance = lambda item: format_html(
            "<h6>{} - {} to {}</h6><small>{}{}</small>",
            item,
            item.start_date.strftime("%d %B"),
            item.end_date.strftime("%d %B"),
            Batch.html_formatted_batch_price(item),
            Batch.html_formatted_batch_schedules(item),
        )

    def clean(self):
        batch = self.cleaned_data.get('batch')

        if batch is None:
            raise forms.ValidationError(
                ('Please select a batch'),
                code='invalid_batch_selection'
            )

        return self.cleaned_data
