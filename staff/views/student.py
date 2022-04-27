from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from staff.models import Batch


@login_required(login_url='/staff/login/')
def student_list(request, batch_id):
    batch = Batch.objects.get(pk=batch_id)

    return render(
        request,
        'coding_basics/student/list.html',
        {
            'batch': batch,
            'current_tab': 'students'
        }
    )