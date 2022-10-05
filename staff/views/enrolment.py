import csv
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
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

def create_zoom_breakout_csv(request, batch_id):
    batch_number = Batch.objects.get(pk=batch_id).number
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': f"attachment; filename=\"{batch_number}-zoom-breakout.csv\""},
    )
    zoom_rows = prepare_zoom_breakout_csv_data(batch_id)
    writer = csv.writer(response)

    for zoom_row in zoom_rows:
        writer.writerow(zoom_row)

    return response

def prepare_zoom_breakout_csv_data(batch_id):
    enrolments = Enrolment.objects.filter(batch_id=batch_id)
    headers = ['Pre-assign Room Name', 'Email Address']
    zoom_rows = [headers]

    for enrolment in enrolments:
        zoom_row = [f"room{enrolment.section.number}", enrolment.student_user.email]
        zoom_rows.append(zoom_row)

    return zoom_rows
