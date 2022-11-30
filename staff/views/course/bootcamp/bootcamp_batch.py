from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views import View

from staff.forms import BatchForm, SectionForm, BatchScheduleFormSet
from staff.models import Batch, BatchSchedule, Course, Section


class ListView(LoginRequiredMixin, View):
    def get(self, request):
        batch_queryset = Batch.bootcamp_objects.all().order_by('-number')

        return render(
            request,
            'course/bootcamp/batch/list.html',
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
            'course/bootcamp/batch/detail.html',
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
            'course/bootcamp/batch/new.html',
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
                    return redirect('bootcamp_batch_detail', batch_id=batch.id)
            except IntegrityError:
                return redirect('bootcamp_batch_new')
        return HttpResponse(status=200)

class EditView(LoginRequiredMixin, View):
    def get(self, request, batch_id):
        batch = Batch.bootcamp_objects.get(pk=batch_id)
        section = Section.objects.filter(batch__id=batch_id).first()
        batchschedule_queryset = BatchSchedule.objects.filter(batch__id=batch_id)

        batch_form = BatchForm(instance=batch)
        section_form = SectionForm(instance=section)
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
            'course/bootcamp/batch/edit.html',
            {
                'batch': batch,
                'batch_form': batch_form,
                'section_form': section_form,
                'batch_schedule_formset': batch_schedule_formset
            }
        )

    def post(self, request, batch_id):
        batch = Batch.bootcamp_objects.get(pk=batch_id)
        section_queryset = Section.objects.filter(batch__id=batch.id)

        batch_form = BatchForm(request.POST)
        section_form = SectionForm(request.POST)
        batch_schedule_formset = BatchScheduleFormSet(
            request.POST,
            prefix='batch-schedule'
        )

        if batch_form.is_valid() and section_form.is_valid() and batch_schedule_formset.is_valid():
            sections = batch_form.cleaned_data.get('sections')
            section_capacity = section_form.cleaned_data.get('capacity')

            validate_batch_sections(batch_form, int(sections), section_queryset.count())
            validate_section_capacity(section_form, int(section_capacity), section_queryset.first().capacity)

            try:
                with transaction.atomic():
                    batch.start_date = batch_form.cleaned_data.get('start_date')
                    batch.end_date = batch_form.cleaned_data.get('end_date')
                    batch.sections = sections
                    batch.capacity = sections * section_capacity
                    batch.price = batch_form.cleaned_data.get('price')
                    batch.type = batch_form.cleaned_data.get('type')
                    batch.save()

                    for section_number in range(Section.next_number(batch_id), sections + 1):
                        Section.objects.create(
                            batch=batch,
                            number=section_number,
                            capacity=section_capacity,
                        )
                    section_queryset.update(capacity=section_capacity)

                    BatchSchedule.objects.filter(batch__id=batch.id).delete()
                    BatchSchedule.objects.bulk_create(new_batch_schedules(batch, batch_schedule_formset))

                    return redirect('bootcamp_batch_detail', batch_id=batch.id)
            except IntegrityError:
                return redirect('bootcamp_batch_edit', batch_id=batch.id)
        return render(
            request,
            'course/bootcamp/batch/edit.html',
            {
                'batch': batch,
                'batch_form': batch_form,
                'section_form': section_form,
                'batch_schedule_formset': batch_schedule_formset
            }
        )

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
