from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound
from django.shortcuts import render

from staff.models import Batch, Section


@login_required(login_url='/staff/login/')
def section_list(request, batch_id):
    batch = Batch.objects.get(pk=batch_id)
    sections_queryset = Section.objects.filter(batch__pk=batch_id)

    return render(
        request,
        'basics/section/list.html',
        {
            'batch': batch,
            'sections': sections_queryset,
            'current_tab': 'sections'
        }
    )


@login_required(login_url='/staff/login/')
def section_detail(request, batch_id, section_id):
    batch = Batch.objects.get(pk=batch_id)
    section = Section.objects.get(pk=section_id)

    if batch is None or section is None:
        return HttpResponseNotFound('Error: Batch and/or section does not exist')

    return render(
        request,
        'basics/section/overview.html',
        {
            'batch': batch,
            'section': section,
            'current_tab': 'overview'
        }
    )
