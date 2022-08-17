from django import forms

from staff.models import Course

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name']
        widgets = {'name': forms.Select()}
        labels = {'name': Course.__name__}
