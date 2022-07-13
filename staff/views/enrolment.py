from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View

from staff.models import Batch
from student.models.enrolment import Enrolment


class ListView(LoginRequiredMixin, View):
    def get(self, request, batch_id):
        enrolment_queryset = Enrolment.objects.filter(batch_id=batch_id)
        batch = Batch.objects.get(pk=batch_id)

        return render(
            request,
            'basics/enrolment/list.html',
            {
                'batch': batch,
                'enrolments': enrolment_queryset,
                'current_tab': 'enrolments',
            }
        )
