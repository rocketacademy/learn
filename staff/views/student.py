from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from itertools import chain

from authentication.models import StudentUser
from staff.models import Batch
from student.models.enrolment import Enrolment


class ListView(LoginRequiredMixin, View):
    def get(self, request, batch_id):
        student_user_queryset = StudentUser.objects.filter(enrolment__in=Enrolment.objects.filter(batch_id=batch_id))
        batch = Batch.objects.get(pk=batch_id)

        return render(
            request,
            'basics/student/list.html',
            {
                'batch': batch,
                'current_tab': 'students',
                'student_user_queryset': student_user_queryset
            }
        )
