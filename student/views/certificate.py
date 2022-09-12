from django.shortcuts import render
from django.views import View

from staff.models.certificate import Certificate

class DetailView(View):
    def get(self, request, certificate_credential):
        certificate = Certificate.objects.get(credential=certificate_credential)

        return render(
            request,
            'certificate/detail.html',
            {
                'certificate': certificate
            }
        )
