from django import forms
from ..models import Batch


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
