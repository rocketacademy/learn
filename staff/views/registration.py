from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View

from staff.models import Batch
from student.models.registration import Registration


class ListView(LoginRequiredMixin, View):
    def get(self, request, batch_id):
        registration_queryset = Registration.objects.filter(batch_id=batch_id)
        batch = Batch.basics_objects.get(pk=batch_id)

        return render(
            request,
            'basics/registration/list.html',
            {
                'batch': batch,
                'registrations': registration_queryset,
                'current_tab': 'registrations',
            }
        )
