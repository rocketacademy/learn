from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.http import HttpResponseRedirect
from django.shortcuts import render

from staff.forms import BatchForm, BatchScheduleFormSet
from staff.models import Batch, BatchSchedule, Course, Section


@login_required(login_url='/staff/login/')
def batch_list(request):
    if request.method == 'GET':
        batch_queryset = Batch.objects.all().order_by('-number')

        return render(
            request,
            'basics/batch/list.html',
            {
                'batches': batch_queryset,
            }
        )

@login_required(login_url='/staff/login/')
def batch_new(request):
    latest_batch_number = Batch.objects.aggregate(Max('number'))

    if latest_batch_number['number__max']:
        next_batch_number = latest_batch_number['number__max'] + 1
    else:
        next_batch_number = 1

    if request.method == 'GET':
        batch_form = BatchForm(None)
        batch_schedule_formset = BatchScheduleFormSet(prefix='batch-schedule')

        return render(
            request,
            'basics/batch/new.html',
            {
                'next_batch_number': next_batch_number,
                'batch_form': batch_form,
                'batch_schedule_formset': batch_schedule_formset
            }
        )
    elif request.method == 'POST':
        batch_form = BatchForm(request.POST)
        batch_schedule_formset = BatchScheduleFormSet(request.POST, prefix='batch-schedule')

        if batch_form.is_valid() and batch_schedule_formset.is_valid():
            sections = batch_form.cleaned_data.get('sections')
            section_capacity = batch_form.cleaned_data.get('section_capacity')
            total_batch_schedule_forms = int(request.POST['batch-schedule-TOTAL_FORMS'])

            batch = Batch.objects.create(
                course=Course.objects.get(name=settings.CODING_BASICS),
                capacity=sections * section_capacity,
                start_date=batch_form.cleaned_data.get('start_date'),
                end_date=batch_form.cleaned_data.get('end_date'),
                sections=sections
            )
            for number in range(1, sections + 1):
                Section.objects.create(
                    batch=batch,
                    number=number,
                    capacity=section_capacity
                )
            for index in range(total_batch_schedule_forms):
                BatchSchedule.objects.create(
                    batch=batch,
                    day=request.POST[f"batch-schedule-{index}-day"],
                    start_time=request.POST[f"batch-schedule-{index}-start_time"],
                    end_time=request.POST[f"batch-schedule-{index}-end_time"]
                )

            return HttpResponseRedirect('/staff/basics/batches/')

        return render(
            request,
            'basics/batch/new.html',
            {
                'next_batch_number': next_batch_number,
                'batch_form': batch_form,
                'batch_schedule_formset': batch_schedule_formset
            }
        )

@login_required(login_url='/staff/login/')
def batch_detail(request, batch_id):
    batch = Batch.objects.get(pk=batch_id)

    return render(
        request,
        'basics/batch/detail.html',
        {
            'batch': batch,
            'current_tab': 'overview'
        }
    )
