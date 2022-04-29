from django.forms import ModelForm, TimeInput, Select, ValidationError

from staff.models import BatchSchedule

class BatchScheduleForm(ModelForm):
    class Meta:
        model = BatchSchedule
        fields = [
            'day',
            'start_time',
            'end_time',
            'batch'
        ]
        widgets = {
            'day': Select(attrs={'class': 'form-control'}),
            'start_time': TimeInput(attrs={'type': 'time'}),
            'end_time': TimeInput(attrs={'type': 'time'})
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time and start_time <= end_time:
            message = ValidationError(('Start time must be before end time'), code='invalid_time')
            self.add_error('start_time', message)
            self.add_error('end_time', message)
