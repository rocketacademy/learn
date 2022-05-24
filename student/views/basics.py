from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from formtools.wizard.views import SessionWizardView

from authentication.models import User
from staff.models import batch
from staff.models.batch import Batch
from student.forms.registration.basics import BatchSelectionForm, StudentInfoForm
from student.models.enrolment import Enrolment


class RegistrationWizard(SessionWizardView):
    template_name = 'basics/registration/form.html'
    form_list = (
        ('batch_selection', BatchSelectionForm),
        ('student_info', StudentInfoForm)
    )

    def done(self, form_list, **kwargs):
        do_something_with_form_list(form_list)

        return HttpResponseRedirect('/student/basics/register/confirmation/')

class ConfirmationView(View):
    def get(self, request):
        return render(
            request,
            'basics/registration/confirmation.html'
        )

def do_something_with_form_list(form_list):
    pass
