import datetime
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.forms import formset_factory

from staff.forms import BatchForm
from staff.models import Batch, Course, Section


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

def batch_new(request):
    if request.method == 'GET':
        latest_batch_number = Batch.objects.latest('number').number
        batch_form = BatchForm(None)

        if latest_batch_number:
            next_batch_number = latest_batch_number + 1
        else:
            next_batch_number = 1

        return render(
            request,
            'basics/batch/new.html',
            {
                'next_batch_number': next_batch_number,
                'batch_form': batch_form,
            }
        )
    elif request.method == 'POST':
        batch_form = BatchForm(request.POST)

        if not batch_form.is_valid():
            return render(
                request,
                'basics/batch/new.html',
                {
                    'batch_form': batch_form,
                }
            )

        course = Course.objects.get(name=settings.CODING_BASICS)
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        sections = int(request.POST['sections'])
        section_capacity = int(request.POST['section_capacity'])
        batch_capacity = sections * section_capacity

        batch = Batch.objects.create(
            course=course,
            capacity=batch_capacity,
            start_date=start_date,
            end_date=end_date,
            sections=sections
        )
        for number in range(1, sections + 1):
            Section.objects.create(
                batch=batch,
                number=number,
                capacity=section_capacity
            )
        return HttpResponseRedirect('/staff/basics/batches/')


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
