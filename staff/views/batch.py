from datetime import date, timedelta
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import View
from sendgrid.helpers.mail import To
from sentry_sdk import capture_exception, capture_message
from urllib.parse import urlencode

from emails.library.sendgrid import Sendgrid
from payment.models import ReferralCoupon
from staff.forms import BatchForm, SectionForm, BatchScheduleFormSet
from staff.forms.basics_graduation import BasicsGraduationForm
from staff.models import Batch, BatchSchedule, Certificate, Course, Section
from student.library.slack import Slack
from student.models.enrolment import Enrolment

class ListView(LoginRequiredMixin, View):
    def get(self, request):
        batch_queryset = Batch.objects.all().order_by('-number')

        return render(
            request,
            'basics/batch/list.html',
            {
                'batches': batch_queryset,
            }
        )

class DetailView(LoginRequiredMixin, View):
    def get(self, request, batch_id):
        batch = Batch.objects.get(pk=batch_id)
        section_capacity = Section.objects.filter(batch__id=batch_id).first().capacity
        batchschedule_queryset = BatchSchedule.objects.filter(batch__id=batch_id)

        return render(
            request,
            'basics/batch/detail.html',
            {
                'current_tab': 'overview',
                'batch': batch,
                'section_capacity': section_capacity,
                'batch_schedules': batchschedule_queryset
            }
        )

class NewView(LoginRequiredMixin, View):
    def get(self, request):
        course_id = Course.objects.get(name=settings.CODING_BASICS).id
        next_batch_number = Batch.next_number(course_id)
        batch_form = BatchForm(None)
        section_form = SectionForm(None)
        batch_schedule_formset = BatchScheduleFormSet(prefix='batch-schedule')

        return render(
            request,
            'basics/batch/new.html',
            {
                'next_batch_number': next_batch_number,
                'batch_form': batch_form,
                'section_form': section_form,
                'batch_schedule_formset': batch_schedule_formset
            }
        )

    def post(self, request):
        course = Course.objects.get(name=settings.CODING_BASICS)
        batch_form = BatchForm(request.POST)
        section_form = SectionForm(request.POST)
        batch_schedule_formset = BatchScheduleFormSet(request.POST, prefix='batch-schedule')

        if batch_form.is_valid() and section_form.is_valid() and batch_schedule_formset.is_valid():
            sections = batch_form.cleaned_data.get('sections')
            section_capacity = section_form.cleaned_data.get('capacity')

            try:
                with transaction.atomic():
                    batch = Batch.objects.create(
                        course=course,
                        capacity=sections * section_capacity,
                        start_date=batch_form.cleaned_data.get('start_date'),
                        end_date=batch_form.cleaned_data.get('end_date'),
                        sections=sections
                    )
                    for section_number in range(1, sections + 1):
                        Section.objects.create(
                            batch=batch,
                            number=section_number,
                            capacity=section_capacity,
                        )
                    for index in range(int(request.POST['batch-schedule-TOTAL_FORMS'])):
                        BatchSchedule.objects.create(
                            batch=batch,
                            day=request.POST[f"batch-schedule-{index}-day"],
                            iso_week_day=settings.ISO_WEEK_DAYS[request.POST[f"batch-schedule-{index}-day"]],
                            start_time=request.POST[f"batch-schedule-{index}-start_time"],
                            end_time=request.POST[f"batch-schedule-{index}-end_time"]
                        )
                    create_batch_slack_channel(batch)

                    return HttpResponseRedirect('/staff/basics/batches/')
            except IntegrityError:
                return redirect('batch_new')
        return render(
            request,
            'basics/batch/new.html',
            {
                'next_batch_number': Batch.next_number(course.id),
                'batch_form': batch_form,
                'section_form': section_form,
                'batch_schedule_formset': batch_schedule_formset
            }
        )

class EditView(LoginRequiredMixin, View):
    def get(self, request, batch_id):
        batch = Batch.objects.get(pk=batch_id)
        section_queryset = Section.objects.filter(batch__id=batch.id)
        batchschedule_queryset = BatchSchedule.objects.filter(batch__id=batch.id)

        batch_form = BatchForm(instance=batch)
        section_form = SectionForm(instance=section_queryset.first())
        batch_schedule_formset = BatchScheduleFormSet(
            initial=[{
                'day': schedule.day,
                'start_time': schedule.start_time,
                'end_time': schedule.end_time
            } for schedule in batchschedule_queryset],
            prefix='batch-schedule'
        )

        return render(
            request,
            'basics/batch/edit.html',
            {
                'current_tab': 'overview',
                'batch': batch,
                'batch_form': batch_form,
                'section_form': section_form,
                'batch_schedule_formset': batch_schedule_formset
            }
        )

    def post(self, request, batch_id):
        batch = Batch.objects.get(pk=batch_id)
        section_queryset = Section.objects.filter(batch__id=batch.id)

        batch_form = BatchForm(request.POST)
        section_form = SectionForm(request.POST)
        batch_schedule_formset = BatchScheduleFormSet(
            request.POST,
            prefix='batch-schedule'
        )

        validate_batch_sections(batch_form, int(request.POST['sections']), section_queryset.count())
        validate_section_capacity(section_form, int(request.POST['capacity']), section_queryset.first().capacity)

        if batch_form.is_valid() and section_form.is_valid() and batch_schedule_formset.is_valid():
            sections = batch_form.cleaned_data.get('sections')
            section_capacity = section_form.cleaned_data.get('capacity')

            try:
                with transaction.atomic():
                    batch.start_date = batch_form.cleaned_data.get('start_date')
                    batch.end_date = batch_form.cleaned_data.get('end_date')
                    batch.sections = sections
                    batch.capacity = sections * section_capacity
                    batch.save()
                    slack_client = Slack()

                    for section_number in range(Section.next_number(batch_id), sections + 1):
                        section = Section.objects.create(
                            batch=batch,
                            number=section_number,
                            capacity=section_capacity,
                        )
                        slack_channel_name = f"{batch.number}-{section.number}"
                        cutoff_date = batch.start_date - timedelta(days=settings.DAYS_BEFORE_BATCH_FOR_ADDING_STUDENTS_TO_SECTION_CHANNELS)

                        if date.today() > cutoff_date:
                            slack_channel_id = slack_client.create_channel(slack_channel_name)
                            section.slack_channel_id = slack_channel_id
                            section.save()
                    section_queryset.update(capacity=section_capacity)

                    BatchSchedule.objects.filter(batch__id=batch.id).delete()
                    BatchSchedule.objects.bulk_create(new_batch_schedules(batch, batch_schedule_formset))

                    return redirect('batch_detail', batch_id=batch.id)
            except IntegrityError:
                return redirect('batch_edit', batch_id=batch.id)
        return render(
            request,
            'basics/batch/edit.html',
            {
                'current_tab': 'overview',
                'batch': batch,
                'batch_form': batch_form,
                'section_form': section_form,
                'batch_schedule_formset': batch_schedule_formset
            }
        )

class GraduateView(LoginRequiredMixin, View):
    def get(self, request, batch_id):
        batch = Batch.objects.get(pk=batch_id)
        basics_graduation_form = BasicsGraduationForm(batch_id=batch_id)

        if batch.has_ended():
            return render(
                request,
                'basics/batch/graduate.html',
                {
                    'batch': batch,
                    'basics_graduation_form': basics_graduation_form
                }
            )

        return redirect('batch_detail', batch_id=batch_id)

    def post(self, request, batch_id):
        basics_graduation_form = BasicsGraduationForm(request.POST, batch_id=batch_id)

        if basics_graduation_form.is_valid():
            enrolment_queryset = Enrolment.objects.filter(id__in=basics_graduation_form.cleaned_data.get('enrolment'))
            to_emails = []

            try:
                with transaction.atomic():
                    enrolment_queryset.update(status=Enrolment.PASSED)
                    for enrolment in enrolment_queryset:
                        student_user = enrolment.student_user
                        certificate = Certificate.objects.create(
                            enrolment=enrolment,
                            graduation_date=date.today()
                        )
                        referral_coupon = ReferralCoupon.objects.create(
                            start_date=timezone.now(),
                            referrer=enrolment.student_user
                        )
                        certificate_url = reverse(
                            'basics_certificate',
                            kwargs={'certificate_credential': certificate.credential}
                        )

                        to_emails.append(
                            To(
                                email=student_user.email,
                                name=student_user.first_name,
                                dynamic_template_data={
                                    'first_name': student_user.first_name.capitalize(),
                                    'certificate_url': certificate_url,
                                    'add_to_linkedin_url': add_to_linkedin_url(certificate, certificate_url),
                                    'referral_coupon_code': referral_coupon.code
                                }
                            )
                        )
                    sendgrid_client = Sendgrid()
                    sendgrid_client.send_bulk(
                        settings.ROCKET_CODING_BASICS_EMAIL,
                        to_emails,
                        settings.CODING_BASICS_GRADUATION_NOTIFICATION_TEMPLATE_ID
                    )
            except Exception as error:
                capture_message(f"Exception when processing graduation for Batch {batch_id}")
                capture_exception(error)
        return redirect('enrolment_list', batch_id=batch_id)

def validate_batch_sections(batch_form, new_number_of_sections, current_number_of_sections):
    if new_number_of_sections < current_number_of_sections:
        batch_form.add_error(
            'sections',
            f"This batch should have at least {current_number_of_sections} sections"
        )

def validate_section_capacity(section_form, new_section_capacity, current_section_capacity):
    if new_section_capacity < current_section_capacity:
        section_form.add_error(
            'capacity',
            f"The sections in this batch should have a capacity of at least {current_section_capacity}"
        )

def new_batch_schedules(batch, batch_schedule_formset):
    new_batch_schedules = []
    for form in batch_schedule_formset:
        day = form.cleaned_data.get('day')
        start_time = form.cleaned_data.get('start_time')
        end_time = form.cleaned_data.get('end_time')

        if day and start_time and end_time:
            new_batch_schedules.append(
                BatchSchedule(
                    batch=batch,
                    day=day,
                    iso_week_day=settings.ISO_WEEK_DAYS[form.cleaned_data.get('day')],
                    start_time=start_time,
                    end_time=end_time
                )
            )

    return new_batch_schedules

def create_batch_slack_channel(batch):
    slack_client = Slack()
    slack_channel_name = f"{batch.number}-all"

    slack_channel_id = slack_client.create_channel(slack_channel_name)
    batch.slack_channel_id = slack_channel_id
    batch.save()

def add_to_linkedin_url(certificate, certificate_url):
    params = {
        'startTask': certificate.enrolment.batch.course.name,
        'name': certificate.enrolment.batch.course.get_name_display(),
        'organizationName': settings.ROCKET_ACADEMY,
        'issueYear': certificate.graduation_date.year,
        'issueMonth': certificate.graduation_date.month,
        'certUrl': certificate_url
    }

    url_encoded_params = urlencode(params, doseq=True)

    return f"https://www.linkedin.com/profile/add?{url_encoded_params}"
