from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render
from .models import Batch, Section, Course, BatchSchedule
from .forms import AddBatchForm
from .forms import LoginForm
import datetime

def index(request):
    return HttpResponseRedirect('/staff/coding-basics/batches/')

def login_view(request):
    if request.method == 'GET':
        form = LoginForm(None)
        
        return render(request, 'login.html', {'form': form})
    elif request.method == 'POST':
        form = LoginForm(request.POST)

        if not form.is_valid():
            return render(request, 'login.html', {'form': form})

        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')

        user = authenticate(request, email=email, password=password)
        if user == None:
            form.add_error('password', 'The password you entered was incorrect')

            return render(request, 'login.html', {'form': form})

        login(request, user)
        return HttpResponseRedirect('/staff/coding-basics/batches/')

@login_required(login_url='/staff/login/')
def batches_view(request):
    course = Course.objects.get(name="CODING_BASICS")
    batches = Batch.objects.all().order_by("-number")
    latest_batch_number = 0
    batch_schedules = BatchSchedule.objects.all()

    batch_list = list(batches)
    if len(batch_list) > 0:
        latest_batch_number = batch_list[0].number

    if request.method == "GET":
        add_batch_form = AddBatchForm()
    else:
        add_batch_form = AddBatchForm(request.POST)
        
        if add_batch_form.is_valid():
            new_batch = add_batch_form.save()

            batchInfoDict = dict(request.POST)

            # iterate through create batch info
            for key in batchInfoDict:
                # look for course day times
                if "course-day-time" in key:
                    # make entry into BatchSchedules table
                    batch_schedule_entry = BatchSchedule.objects.create(
                        batch=new_batch,
                        course_day=batchInfoDict[key][0].upper(),
                        start_time=datetime.datetime.strptime(batchInfoDict[key][1], "%H:%M"),
                        end_time=datetime.datetime.strptime(batchInfoDict[key][2], "%H:%M"),
                    )
                   

    context = {
        "batches": batches,
        "course": course,
        "form": add_batch_form,
        "next_batch_number": latest_batch_number + 1,
        "batch_schedules": batch_schedules,
    }

    return render(request, "coding_basics/admin/all-batches.html", context)

@login_required(login_url='/staff/login/')
def batch_view(request, batch_id):
    batch_queryset = Batch.objects.filter(pk=batch_id)

    if not batch_queryset.exists():
        return HttpResponseNotFound

    return render(request,
        'coding_basics/batch/overview.html',
        {
            'batch': batch_queryset.last(),
            'current_tab': 'overview'
        }
    )

@login_required(login_url='/staff/login/')
def students_view(request, batch_id):
    batch_queryset = Batch.objects.filter(pk=batch_id)

    if not batch_queryset.exists():
        return HttpResponseNotFound

    return render(request,
        'coding_basics/batch/students.html',
        {
            'batch': batch_queryset.last(),
            'current_tab': 'students'
        }
    )

@login_required(login_url='/staff/login/')
def sections_view(request, batch_id):
    batch_queryset = Batch.objects.filter(pk=batch_id)
    sections_queryset = Section.objects.filter(batch__pk=batch_id)

    if not batch_queryset.exists() or not sections_queryset.exists():
        return HttpResponseNotFound

    return render(request,
        'coding_basics/batch/sections.html',
        {
            'batch': batch_queryset.last(),
            'sections': sections_queryset,
            'current_tab': 'sections'
        }
    )

@login_required(login_url='/staff/login/')
def section_view(request, batch_id, section_id):
    batch_queryset = Batch.objects.filter(pk=batch_id)
    sections_queryset = Section.objects.filter(pk=section_id)

    if not batch_queryset.exists() or not sections_queryset.exists():
        return HttpResponseNotFound

    return render(request,
        'coding_basics/section/overview.html',
        {
            'batch': batch_queryset.last(),
            'section': sections_queryset.last(),
            'current_tab': 'overview'
        }
    )

@login_required(login_url='/staff/login/')
def section_leaders_view(request):
    return render(request,
        'coding_basics/admin/section-leaders.html',
    )