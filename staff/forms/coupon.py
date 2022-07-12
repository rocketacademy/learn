from django import forms

from payment.models.coupon import Coupon

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = [
            'start_date',
            'end_date',
            'type',
            'discount_type',
            'discount_amount',
            'description'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'type': forms.Select(),
            'discount_type': forms.Select(),
            'discount_amount': forms.NumberInput,
            'description': forms.Textarea(attrs={'rows': 2})
        }

    def clean(self):
        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')

        if start_date and end_date and start_date >= end_date:
            message = forms.ValidationError(('Start date must be before end date'), code='invalid_date')
            self.add_error('start_date', message)
            self.add_error('end_date', message)

        return self.cleaned_data

    def clean_discount_amount(self):
        discount_amount = self.cleaned_data.get('discount_amount')

        if discount_amount < 1:
            raise forms.ValidationError(
                ('Discount amount should be greater than zero'),
                code='invalid_discount_amount'
            )

        return discount_amount
