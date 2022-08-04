from django import forms

from payment.models.coupon_effect import CouponEffect

class CouponEffectForm(forms.ModelForm):
    class Meta:
        model = CouponEffect
        fields = [
            'discount_type',
            'discount_amount'
        ]
        widgets = {
            'discount_type': forms.Select(),
            'discount_amount': forms.NumberInput()
        }
