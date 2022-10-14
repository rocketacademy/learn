from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View

from staff.forms import BatchForm, SectionForm, BatchScheduleFormSet
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

class NewView(LoginRequiredMixin, View):
    def get(self, request):
        batch_form = BatchForm(None)
        section_form = SectionForm(None)
        batch_schedule_formset = BatchScheduleFormSet(prefix='batch-schedule')

        return render(
            request,
            'bootcamp/batch/new.html',
            {
                'batch_form': batch_form,
                'section_form': section_form,
                'batch_schedule_formset': batch_schedule_formset
            }
        )
