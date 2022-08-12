from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render
from django.views import View
from formtools.wizard.views import SessionWizardView

from authentication.models import StudentUser
from payment.library.stripe import Stripe
from payment.models.coupon import Coupon
from student.models.registration import Registration

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
        referral_code = form_data[1]['referral_code']

        try:
            with transaction.atomic():
                registration = Registration.objects.create(
                    course=batch.course,
                    batch=batch,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    country_of_residence=country_of_residence,
                    referral_channel=referral_channel,
                    referral_code=referral_code
                )

                user_queryset = User.objects.filter(email=email)
                if user_queryset:
                    existing_user = user_queryset.first()
                    form_properties = {
                        'first_name': first_name,
                        'last_name': last_name
                    }

                    if existing_user.requires_update(form_properties) is True:
                        existing_user = user_queryset.first()
                        existing_user.first_name = first_name
                        existing_user.last_name = last_name

                        existing_user.save()
                if not user_queryset:
                    StudentUser.objects.create_user(
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        password=settings.PLACEHOLDER_PASSWORD
                    )

                return redirect(
                    'basics_register_payment_preview',
                    registration_id=registration.id,
                )
        except IntegrityError:
            return redirect('basics_register')


class PaymentPreviewView(View):
    def get(self, request, registration_id):
        registration = Registration.objects.get(pk=registration_id)
        original_payable_amount = settings.CODING_BASICS_REGISTRATION_FEE_SGD
        discount = 0
        stripe_coupon_id = None

        if registration.referral_code:
            coupon = Coupon.objects.get(code=registration.referral_code)
            discount = coupon.biggest_discount_for(registration.course, original_payable_amount)
            stripe_coupon = Stripe().create_coupon(discount)
            stripe_coupon_id = stripe_coupon['id']

        return render(
            request,
            'registration/payment_preview.html',
            {
                'payable_type': Registration.__name__,
                'payable_id': registration_id,
                'payable_line_item_name': 'Registration for Coding Basics',
                'payable_line_item_amount_in_cents': original_payable_amount * 100,
                'original_payable_amount': original_payable_amount,
                'stripe_coupon_id': stripe_coupon_id,
                'final_payable_amount': original_payable_amount - discount,
                'payment_success_path': f"/student/basics/register/{registration_id}/confirmation/",
                'payment_cancel_path': '/student/basics/register/',
            }
        )

class ConfirmationView(View):
    def get(self, request, registration_id):
        registration = Registration.objects.get(pk=registration_id)

        return render(
            request,
            'registration/confirmation.html',
            {
                'registration': registration,
                'slack_invite_link': settings.SLACK_CODING_BASICS_WORKSPACE_INVITE_LINK
            }
        )
