from django import forms

from student.models.enrolment import Enrolment

class GraduationForm(forms.Form):
    enrolment = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(attrs={'checked': ''}),
        required=False,
        initial=True,
        label=''
    )

    def __init__(self, *args, **kwargs):
        batch_id = kwargs.pop('batch_id')
        super(GraduationForm, self).__init__(*args, **kwargs)

        self.fields['enrolment'].choices = [
            (enrolment.id, enrolment.student_user) for enrolment in Enrolment.objects.filter(batch__pk=batch_id, status=Enrolment.ENROLLED)
        ]
