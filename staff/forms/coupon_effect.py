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

    def clean(self):
        discount_amount = self.cleaned_data.get('discount_amount')
        discount_type = self.cleaned_data.get('discount_type')

        if discount_type == 'percent' and discount_amount > 100:
            message = forms.ValidationError(
                ('Discount should not be more than 100%'),
                code='invalid_discount'
            )
            self.add_error('discount_amount', message)
            self.add_error('discount_type', message)

        return self.cleaned_data
