from crispy_forms.helper import FormHelper
from django.forms import BaseFormSet, ModelForm, Select, TimeInput, ValidationError, formset_factory

from staff.models import BatchSchedule

class BatchScheduleForm(ModelForm):
    class Meta:
        model = BatchSchedule
        fields = [
            'day',
            'start_time',
            'end_time'
        ]
        widgets = {
            'day': Select(attrs={'class': 'form-control'}),
            'start_time': TimeInput(attrs={'type': 'time'}),
            'end_time': TimeInput(attrs={'type': 'time'})
        }

    def __init__(self, *args, **kwargs):
        super(BatchScheduleForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False

class BaseBatchScheduleFormSet(BaseFormSet):
    def clean(self):
        if any(self.errors):
            return

        for form in self.forms:
            if form.cleaned_data:
                start_time = form.cleaned_data['start_time']
                end_time = form.cleaned_data['end_time']

                if start_time and end_time and start_time >= end_time:
                    message = ValidationError(('Start time must be before end time'), code='invalid_time')
                    form.add_error('start_time', message)
                    form.add_error('end_time', message)

BatchScheduleFormSet = formset_factory(
    BatchScheduleForm,
    formset=BaseBatchScheduleFormSet,
    max_num=7,
    absolute_max=7
)
