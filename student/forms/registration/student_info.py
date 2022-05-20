from django import forms
import datetime

from authentication.models import User


class StudentInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'})
        }

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')

        if len(first_name) < 2:
            raise forms.ValidationError(
                ('Please enter a valid first name'),
                code='invalid_first_name'
            )

        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')

        if len(last_name) < 2:
            raise forms.ValidationError(
                ('Please enter a valid last name'),
                code='invalid_last_name'
            )

        return last_name
