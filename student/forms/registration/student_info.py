from django import forms

from student.models.registration import Registration


class StudentInfoForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = [
            'first_name',
            'last_name',
            'email',
            'country_of_residence',
            'referral_channel',
            'referral_code'
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
            ),
            'referral_code': forms.TextInput(
                attrs={
                    'class': 'form-control my-1',
                    'id': 'registration-form-referral-code',
                }
            )
        }
        labels = {
            'referral_channel': 'How did you hear about us?'
        }
