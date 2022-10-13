from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View

from staff.models import Batch


class ListView(LoginRequiredMixin, View):
    def get(self, request):
        batch_queryset = Batch.bootcamp_objects.all().order_by('-number')

        return render(
            request,
            'bootcamp/batch/list.html',
            {
                'batches': batch_queryset,
            }
        )