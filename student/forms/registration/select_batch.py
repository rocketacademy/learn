from django import forms
from datetime import datetime

from student.models.enrolments import Enrolment
from staff.models.batch_schedule import BatchSchedule


class BatchRadioSelect(forms.RadioSelect):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)

        num_batch_enrolments = Enrolment.objects.filter(
            batch_id=value.instance.id).count()

        if num_batch_enrolments > value.instance.capacity:
            label_subtext = 'This batch is full'
        else:
            batch_timeslots = BatchSchedule.objects.filter(
                batch_id=value.instance.id)
            label_subtext = 'Every '
            timeslot_count = 0
            for timeslot in batch_timeslots:
                start_time = timeslot.start_time.strftime("%I:%M%p")
                end_time = timeslot.end_time.strftime("%I:%M%p")

                label_subtext += f"{timeslot.day} from {start_time} to {end_time}"
                timeslot_count += 1
                if timeslot_count == batch_timeslots.count() - 1:
                    label_subtext += " and "

        formatted_start_date = datetime.strftime(
            value.instance.start_date, "%d %B %Y")
        formatted_end_date = datetime.strftime(
            value.instance.end_date, "%d %B %Y")

        option['label'] = (
            f"{formatted_start_date} to {formatted_end_date}"
            f"{label_subtext}"
        )
        return option


class SelectBatchForm(forms.ModelForm):

    class Meta:
        model = Enrolment
        fields = [
            'batch',
        ]
        widgets = {
            'batch': BatchRadioSelect()
        }

    def clean(self):
        batch = self.cleaned_data.get('batch')

        if batch is None:
            raise forms.ValidationError(
                ('Please select a batch'),
                code='invalid_batch_selection'
            )

        return self.cleaned_data
