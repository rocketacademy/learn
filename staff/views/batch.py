from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from staff.models import Batch


class ListView(LoginRequiredMixin, View):
    def get(self, request):
        batch_queryset = Batch.objects.all().order_by('-start_date')

        return render(
            request,
            'batch/list.html',
            {
                'batches': batch_queryset,
            }
        )

class DetailView(LoginRequiredMixin, View):
    def get(self, request, batch_id):
        batch = Batch.objects.get(pk=batch_id)

        if batch.is_basics():
            return redirect('basics_batch_detail', batch_id=batch.id)
        elif batch.is_bootcamp():
            return redirect('bootcamp_batch_detail', batch_id=batch.id)
