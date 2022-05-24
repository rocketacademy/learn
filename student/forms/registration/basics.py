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

class StudentInfoForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = [
            'first_name',
            'last_name',
            'email',
            'country_of_residence',
            'referral_channel',
        ]
        widgets = {
            'first_name': forms.TextInput(
                attrs={
                    'class': 'form-control my-1',
                    'id': 'registration-form-first-name',
                    'placeholder': 'Your first name'
                }
            ),
            'last_name': forms.TextInput(
                attrs={
                    'class': 'form-control my-1',
                    'id': 'registration-form-last-name',
                    'placeholder': 'Your last name'
                }
            ),
            'email': forms.TextInput(
                attrs={
                    'class': 'form-control my-1',
                    'id': 'registration-form-email',
                    'placeholder': 'Your email'
                }
            ),
            'country_of_residence': forms.Select(
                attrs={
                    'class': 'form-control my-1',
                    'id': 'registration-form-country-of-residence',
                }
            ),
            'referral_channel': forms.Select(
                attrs={
                    'class': 'form-control my-1',
                    'id': 'registration-form-referral-channel',
                }
            )
        }
