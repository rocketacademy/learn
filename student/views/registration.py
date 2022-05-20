from django.shortcuts import render
from staff.models.batch import Batch
from authentication.models import User
from student.models.enrolments import Enrolment
from student.forms.registration.select_batch import SelectBatchForm
from student.forms.registration.student_info import StudentInfoForm
from formtools.wizard.views import SessionWizardView
from django.views import View


def student_registration(request):
    return render(request, 'registration/student-registration.html')


class StudentRegistrationView(SessionWizardView):
    template_name = 'registration/batch-selection.html'
    form_list = [SelectBatchForm, StudentInfoForm]

    def done(self, form_list, **kwargs):
        form_data = [form.cleaned_data for form in form_list]

        # create user in db
        # TODO: password?
        placeholder_password = 'qwerty1234'
        user = User.objects.create_user(
            form_data[1]['email'], form_data[1]['first_name'], form_data[1]['last_name'], placeholder_password)

        user.save()

        # create new entry in enrolment table
        new_enrolment = Enrolment(batch=form_data[0]['batch'], user=user)
        new_enrolment.save()

        return render(self.request, 'registration/confirmation.html')


class ConfirmationView(View):
    def get(self, request):
        return render(request, 'registration/confirmation.html')
