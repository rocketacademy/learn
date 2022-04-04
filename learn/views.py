from django.shortcuts import redirect

def home(request):
    return redirect('/staff/coding_basics/')