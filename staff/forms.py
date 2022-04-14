from django import forms
from django.contrib.auth import get_user_model
from .models import Batch

User = get_user_model()

class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control mt-5',
                'id': 'login-form-email',
                'placeholder': 'Email'
            }
        ),
        label=''
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'id': 'login-form-password',
                'placeholder': 'Password'
            }
        ),
        label=''
    )

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        queryset = User.objects.filter(email=email)
        if not queryset.exists():
            raise forms.ValidationError(
                ('This email is not registered on Learn'),
                code='unregistered_email',
            )
        
        return email


class AddBatchForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Batch
        fields = '__all__'
        widgets = {"start_date": forms.DateInput(attrs={"type": "date"})}
        widgets = {"end_date": forms.DateInput(attrs={"type": "date"})}


    batch_schedule_1 = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    batch_schedule_2 = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
