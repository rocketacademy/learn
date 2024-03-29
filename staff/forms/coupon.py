from django import forms

from payment.models.coupon import Coupon

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = [
            'start_date',
            'end_date',
            'code',
            'effects',
            'description'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'code': forms.TextInput(),
            'effects': forms.SelectMultiple(),
            'description': forms.Textarea(attrs={'rows': 2})
        }

    def __init__(self, *args, **kwargs):
        super(CouponForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)

        if instance and instance.pk:
            self.fields['code'].widget.attrs['readonly'] = True

    def clean(self):
        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')

        if start_date and end_date and start_date >= end_date:
            message = forms.ValidationError(('Start date must be before end date'), code='invalid_date')
            self.add_error('start_date', message)
            self.add_error('end_date', message)

        return self.cleaned_data
