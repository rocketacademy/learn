from django import forms

from staff.models import Section

class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = [
            'capacity'
        ]
        widgets = {
            'capacity': forms.NumberInput()
        }
        labels = {
            'capacity': 'Section capacity'
        }

    def clean_capacity(self):
        capacity = self.cleaned_data.get('capacity')

        if not capacity > 0:
            raise forms.ValidationError(
                ('Capacity per section should be more than one'),
                code='invalid_capacity',
            )

        return capacity
