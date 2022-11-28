from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.views import View

from authentication.models import StudentUser
from staff.models import Batch, BatchSchedule, Section
from student.models.enrolment import Enrolment


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
        batchschedule_queryset = BatchSchedule.objects.filter(batch__id=batch.id)
        section = Section.objects.get(pk=section_id)
        studentuser_queryset = StudentUser.objects.filter(enrolment__in=Enrolment.objects.filter(section_id=section_id))

        if batch is None or section is None:
            return HttpResponseNotFound('Error: Batch and/or section does not exist')

        return render(
            request,
            'basics/section/detail.html',
            {
                'batch': batch,
                'batch_schedules': batchschedule_queryset,
                'section': section,
                'students': studentuser_queryset,
                'current_tab': 'overview'
            }
        )
