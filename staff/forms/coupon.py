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
