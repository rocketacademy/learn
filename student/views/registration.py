from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from formtools.wizard.views import SessionWizardView

from student.models.registration import Registration
from staff.models import Course

User = get_user_model()

TEMPLATES = {
    'batch_selection': 'registration/batch_selection.html',
    'student_info': 'registration/student_info.html'
}

class RegistrationWizard(SessionWizardView):
    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        form_data = [form.cleaned_data for form in form_list]
        batch = form_data[0]['batch']
        first_name = form_data[1]['first_name'].upper()
        last_name = form_data[1]['last_name'].upper()
        email = form_data[1]['email'].lower()
        country_of_residence = form_data[1]['country_of_residence']
        referral_channel = form_data[1]['referral_channel']

        Registration.objects.create(
            course=batch.course,
            batch=batch,
            first_name=first_name,
            last_name=last_name,
            email=email,
            country_of_residence=country_of_residence,
            referral_channel=referral_channel
        )

        user_queryset = User.objects.filter(email=email)
        if not user_queryset:
            User.objects.create(
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=settings.PLACEHOLDER_PASSWORD
            )

        return HttpResponseRedirect('/student/basics/register/confirmation/')

class ConfirmationView(View):
    def get(self, request):
        return render(
            request,
            'registration/confirmation.html'
        )
