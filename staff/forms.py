import datetime
from django import forms
from django.contrib.auth import get_user_model
from .models import Batch
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

User = get_user_model()


# class LoginForm(forms.Form):
#     email = forms.EmailField(
#         widget=forms.TextInput(
#             attrs={
#                 'class': 'form-control mt-5',
#                 'id': 'login-form-email',
#                 'placeholder': 'Email'
#             }
#         ),
#         label=''
#     )
#     password = forms.CharField(
#         widget=forms.PasswordInput(
#             attrs={
#                 'class': 'form-control',
#                 'id': 'login-form-password',
#                 'placeholder': 'Password'
#             }
#         ),
#         label=''
#     )

#     def clean_email(self):
#         email = self.cleaned_data.get('email').lower()
#         queryset = User.objects.filter(email=email)
#         if not queryset.exists():
#             raise forms.ValidationError(
#                 ('This email is not registered on Learn'),
#                 code='unregistered_email',
#             )

#         return email


# class CreateBatchForm(forms.ModelForm):
#     def __init__(self, *args, **kwargs):
#         super(forms.ModelForm, self).__init__(*args, **kwargs)

#     class Meta:
#         model = Batch
#         fields = ["course", "start_date", "end_date", "sections", "capacity"]
#         widgets = {
#             "course": forms.TextInput(attrs={"type": "hidden", "value": "CODING_BASICS"}),
#             "start_date": forms.DateInput(attrs={"type": "date"}),
#             "end_date": forms.DateInput(attrs={"type": "date"}),
#         }

    # def clean_start_date(self):
    #     start_date = self.cleaned_data.get('start_date')
    #     print('start date', start_date)
    #     print('string start date', str(start_date))

    #     formatted_start_date = datetime.datetime.strptime(str(start_date), "%Y-%m-%d").date()
    #     today = datetime.date.today()

    #     if formatted_start_date > today:
    #         raise forms.ValidationError('Start date cannot be before current date')

    # def check_start_end_dates(self):
    #     print('cleaned data', self.cleaned_data)
    #     end_date = self.cleaned_data.get('end_date')
    #     formatted_end_date = datetime.datetime.strptime(str(end_date), "%Y-%m-%d").date()

    #     start_date = self.cleaned_data.get('start_date')
    #     print('start date', start_date)

    #     formatted_start_date = datetime.datetime.strptime(str(start_date), "%Y-%m-%d").date()

    #     if formatted_start_date > formatted_end_date:
    #         raise forms.ValidationError(
    #             'Start date cannot be after end date'
    #         )

    #     return end_date
