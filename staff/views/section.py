from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.views import View

from staff.models import Batch, Section


class ListView(LoginRequiredMixin, View):
    def get(self, request, batch_id):
        batch = Batch.objects.get(pk=batch_id)
        section_queryset = Section.objects.filter(batch__pk=batch_id).order_by('number')

        return render(
            request,
            'basics/section/list.html',
            {
                'batch': batch,
                'sections': section_queryset,
                'current_tab': 'sections'
            }
        )

class DetailView(LoginRequiredMixin, View):
    def get(self, request, batch_id, section_id):
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
