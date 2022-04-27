import datetime
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render

from staff.models import Batch, Course, BatchSchedule
from staff.forms import CreateBatchForm


@login_required(login_url='/staff/login/')
def batch_list(request):
    course = Course.objects.get(name=settings.CODING_BASICS)
    batch_queryset = Batch.objects.all().order_by('-number')
    latest_batch_number = 0
    batch_schedules = BatchSchedule.objects.all()

    batch_list = list(batch_queryset)
    if len(batch_list) > 0:
        latest_batch_number = batch_list[0].number

    if request.method == 'GET':
        create_batch_form = CreateBatchForm()
    else:
        create_batch_form = CreateBatchForm(request.POST)

        if create_batch_form.is_valid():
            new_batch = create_batch_form.save()
            batch_info_dict = dict(request.POST)

            for key in batch_info_dict:
                if 'course-day-time' in key:
                    BatchSchedule.objects.create(
                        batch=new_batch,
                        course_day=batch_info_dict[key][0].upper(),
                        start_time=datetime.datetime.strptime(batch_info_dict[key][1], '%H:%M'),
                        end_time=datetime.datetime.strptime(batch_info_dict[key][2], '%H:%M'),
                    )

            return HttpResponseRedirect('/staff/basics/batches/')

    context = {
        'course': course,
        'batches': batch_queryset,
        'next_batch_number': latest_batch_number + 1,
        'batch_schedules': batch_schedules,
        'form': create_batch_form,
    }

    return render(request, 'basics/batch/list.html', context)


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
