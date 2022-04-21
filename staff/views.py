from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render
from .models import Batch, Section
from .forms import AddBatchForm

from .forms import LoginForm

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
    batches = Batch.objects.all()

    if request.method == "GET":
        add_batch_form = AddBatchForm()
    else:
        add_batch_form = AddBatchForm(request.POST)
        print(request.POST)
        batch_schedule_1 = request.POST.get('batch_schedule_1')
        print('batcch_schedule_1', batch_schedule_1)
        
        if add_batch_form.is_valid():
            new_batch = add_batch_form.save()
            print(new_batch)

    context = {"batches": batches, "form": add_batch_form}

    return render(request,
        'coding_basics/admin/all-batches.html',
        context
    )

@login_required(login_url='/staff/login/')
def batch_view(request, batch_id):
    batch_queryset = Batch.objects.filter(pk=batch_id)

    if not batch_queryset.exists():
        return HttpResponseNotFound('Error: Batch does not exist')

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