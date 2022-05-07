from django import forms
from django.contrib.auth import get_user_model

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
        user_queryset = User.objects.filter(email=email)
        if not user_queryset.exists():
            raise forms.ValidationError(
                ('This email is not registered on Learn'),
                code='unregistered_email',
            )

        return email
