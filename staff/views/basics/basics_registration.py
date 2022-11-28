from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View

from staff.models import Batch


class ListView(LoginRequiredMixin, View):
    def get(self, request, batch_id):
        batch = Batch.objects.get(pk=batch_id)

        return render(
            request,
            'basics/registration/list.html',
            {
                'batch': batch,
                'registrations': batch.registration_set.all(),
                'current_tab': 'registrations',
            }
        )
