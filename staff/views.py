from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from .forms import LoginForm

def index(request):
    return HttpResponseRedirect('/staff/coding_basics/')

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
        return HttpResponseRedirect('/staff/coding_basics/')

# To-do: Move to CourseViewSet when ready
@login_required(login_url='/staff/login/')
def coding_basics_view(request):
    return HttpResponse('Coding Basics!')

# To-do: Move to BatchViewSet when ready
@login_required(login_url='/staff/login/')
def batch_overview_view(request):
    return render(request,
        'coding_basics/batch/overview.html',
    )

@login_required(login_url='/staff/login/')
def batch_students_view(request):
    return render(request,
        'coding_basics/batch/students.html',
    )

@login_required(login_url='/staff/login/')
def batch_sections_view(request):
    return render(request,
        'coding_basics/batch/sections.html',
    )