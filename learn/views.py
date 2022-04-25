from django.http import HttpResponseRedirect


def home(request):
    return HttpResponseRedirect('/staff/coding-basics/batches/')
