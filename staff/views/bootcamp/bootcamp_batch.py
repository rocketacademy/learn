from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from staff.forms import BatchForm, SectionForm, BatchScheduleFormSet
from staff.models import Batch, BatchSchedule, Course, Section


class ListView(LoginRequiredMixin, View):
    def get(self, request):
        batch_queryset = Batch.bootcamp_objects.all().order_by('-number')

        return render(
            request,
            'bootcamp/batch/list.html',
            {
                'batches': batch_queryset,
            }
        )

class DetailView(LoginRequiredMixin, View):
    def get(self, request, batch_id):
        batch = Batch.bootcamp_objects.get(pk=batch_id)
        section_capacity = Section.objects.filter(batch__id=batch_id).first().capacity
        batchschedule_queryset = BatchSchedule.objects.filter(batch__id=batch_id)

        return render(
            request,
            'bootcamp/batch/detail.html',
            {
                'current_tab': 'overview',
                'batch': batch,
                'section_capacity': section_capacity,
                'batch_schedules': batchschedule_queryset
            }
        )

class NewView(LoginRequiredMixin, View):
    def get(self, request):
        batch_form = BatchForm(None)
        section_form = SectionForm(None)
        batch_schedule_formset = BatchScheduleFormSet(prefix='batch-schedule')

        return render(
            request,
            'bootcamp/batch/new.html',
            {
                'batch_form': batch_form,
                'section_form': section_form,
                'batch_schedule_formset': batch_schedule_formset
            }
        )

    def post(self, request):
        batch_form = BatchForm(request.POST)
        section_form = SectionForm(request.POST)
        batch_schedule_formset = BatchScheduleFormSet(request.POST, prefix='batch-schedule')

        if batch_form.is_valid() and section_form.is_valid() and batch_schedule_formset.is_valid():
            start_date = batch_form.cleaned_data.get('start_date')
            end_date = batch_form.cleaned_data.get('end_date')
            sections = batch_form.cleaned_data.get('sections')
            section_capacity = section_form.cleaned_data.get('capacity')
            price = batch_form.cleaned_data.get('price')
            type = batch_form.cleaned_data.get('type')
            batch_schedules = batch_schedule_formset.cleaned_data

            try:
                with transaction.atomic():
                    course = Course.objects.get(name=Course.CODING_BOOTCAMP)
                    batch = Batch.objects.create(
                        course=course,
                        start_date=start_date,
                        end_date=end_date,
                        capacity=sections * section_capacity,
                        sections=sections,
                        price=price,
                        type=type,
                    )
                    for section_number in range(1, sections + 1):
                        Section.objects.create(
                            batch=batch,
                            number=section_number,
                            capacity=section_capacity
                        )
                    for batch_schedule in batch_schedules:
                        BatchSchedule.objects.create(
                            batch=batch,
                            day=batch_schedule['day'],
                            iso_week_day=settings.ISO_WEEK_DAYS[batch_schedule['day']],
                            start_time=batch_schedule['start_time'],
                            end_time=batch_schedule['end_time']
                        )
                    return HttpResponseRedirect(reverse('bootcamp_batch_list'))
            except IntegrityError:
                return redirect('basics_batch_new')
        return HttpResponse(status=200)
