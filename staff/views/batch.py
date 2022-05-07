from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.shortcuts import render

from staff.forms import BatchForm, SectionForm, BatchScheduleFormSet
from staff.models import Batch, BatchSchedule, Course, Section


@login_required(login_url='/staff/login/')
def list(request):
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
def new(request):
    course_id = Course.objects.get(name=settings.CODING_BASICS).id
    next_batch_number = Batch.next_number(course_id)

    if request.method == 'GET':
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
    elif request.method == 'POST':
        batch_form = BatchForm(request.POST)
        section_form = SectionForm(request.POST)
        batch_schedule_formset = BatchScheduleFormSet(request.POST, prefix='batch-schedule')

        if batch_form.is_valid() and section_form.is_valid() and batch_schedule_formset.is_valid():
            sections = batch_form.cleaned_data.get('sections')
            section_capacity = section_form.cleaned_data.get('capacity')
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
                'section_form': section_form,
                'batch_schedule_formset': batch_schedule_formset
            }
        )

@login_required(login_url='/staff/login/')
def detail(request, batch_id):
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

@login_required(login_url='/staff/login/')
def edit(request, batch_id):
    batch = Batch.objects.get(pk=batch_id)
    section_queryset = Section.objects.filter(batch__id=batch_id)
    batchschedule_queryset = BatchSchedule.objects.filter(batch__id=batch_id)
    # batch_schedules = [{
    #     'day': schedule.day,
    #     'start_time': schedule.start_time,
    #     'end_time': schedule.end_time
    # } for schedule in batchschedule_queryset]

    batch_form = BatchForm(instance=batch)
    section_form = SectionForm(instance=section_queryset.first())
    # batch_schedule_formset = BatchScheduleFormSet(
    #     initial=batch_schedules,
    #     prefix='batch-schedule'
    # )

    if request.method == 'GET':
        return render(
            request,
            'basics/batch/edit.html',
            {
                'current_tab': 'overview',
                'batch': batch,
                'batch_form': batch_form,
                'section_form': section_form,
                # 'batch_schedule_formset': batch_schedule_formset
            }
        )
    elif request.method == 'POST':
        batch_form = BatchForm(request.POST)
        section_form = SectionForm(request.POST)

        new_number_of_sections = int(request.POST['sections'])
        current_number_of_sections = section_queryset.count()
        if new_number_of_sections < current_number_of_sections:
            batch_form.add_error(
                'sections',
                f"This batch should have at least {current_number_of_sections} sections"
            )

        new_section_capacity = int(request.POST['capacity'])
        current_section_capacity = section_queryset.first().capacity
        if new_section_capacity < current_section_capacity:
            section_form.add_error(
                'capacity',
                f"The sections in this batch should have a capacity of at least {current_section_capacity}"
            )

        if batch_form.is_valid() and section_form.is_valid():
            sections = batch_form.cleaned_data.get('sections')
            section_capacity = section_form.cleaned_data.get('capacity')

            batch.start_date = batch_form.cleaned_data.get('start_date')
            batch.end_date = batch_form.cleaned_data.get('end_date')
            batch.sections = sections
            batch.capacity = sections * section_capacity
            batch.save()

            next_section_number = Section.next_number(batch_id)
            for number in range(next_section_number, sections + 1):
                Section.objects.create(
                    batch=batch,
                    number=number,
                    capacity=section_capacity
                )
            section_queryset.update(capacity=section_capacity)

            return redirect('batch_detail', batch_id=batch.id)

        return render(
            request,
            'basics/batch/edit.html',
            {
                'current_tab': 'overview',
                'batch': batch,
                'batch_form': batch_form,
                'section_form': section_form,
            }
        )
