from django import forms

from student.models.enrolment import Enrolment

class BasicsGraduationForm(forms.Form):
    student_user = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(attrs={'checked': ''}),
        required=False,
        initial=True,
        label=''
    )

    def __init__(self, *args, **kwargs):
        batch_id = kwargs.pop('batch_id')
        super(BasicsGraduationForm, self).__init__(*args, **kwargs)

        self.fields['student_user'].choices = [
            (enrolment.id, enrolment.student_user) for enrolment in Enrolment.objects.filter(batch__pk=batch_id)
        ]