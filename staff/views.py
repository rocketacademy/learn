from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

def index(request):
    return render(request, 'login.html')

def login_view(request):
    return render(request, 'login.html')

@login_required(login_url='/staff/login/')
def coding_basics(request):
    return HttpResponse('Coding Basics!')