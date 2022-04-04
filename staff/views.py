from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .forms import LoginForm

def index(request):
    return redirect(coding_basics_view)

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
        return redirect(coding_basics_view)

@login_required(login_url='/staff/login/')
def coding_basics_view(request):
    return HttpResponse('Coding Basics!')