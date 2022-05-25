from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from formtools.wizard.views import SessionWizardView


TEMPLATES = {
    'batch_selection': 'basics/registration/batch_selection.html',
    'student_info': 'basics/registration/student_info.html'
}

class RegistrationWizard(SessionWizardView):
    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

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
