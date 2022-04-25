from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url='/staff/login/')
def section_leader_list(request):
    return render(
        request,
        'coding_basics/section_leader/list.html',
    )
