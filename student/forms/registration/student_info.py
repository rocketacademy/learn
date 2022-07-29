from django.utils.timezone import now
from django import forms

from payment.models.coupon import Coupon
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
            ),
        }
        labels = {
            'referral_channel': 'How did you hear about us?'
        }

    def clean_referral_code(self):
        referral_code = self.cleaned_data.get('referral_code')
        if referral_code is None:
            return referral_code

        coupons = Coupon.objects.filter(code=referral_code)
        if not coupons:
            raise forms.ValidationError(
                ('Referral code is invalid'),
                code='referral_code',
            )

        coupon = coupons.first()
        if coupon.start_date and now() < coupon.start_date:
            raise forms.ValidationError(
                ('Referral code is not in effect yet'),
                code='referral_code',
            )
        if coupon.end_date and now() > coupon.end_date:
            raise forms.ValidationError(
                ('Referral code has expired'),
                code='referral_code',
            )

        return referral_code
