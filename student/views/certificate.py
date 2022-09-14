from django.shortcuts import redirect, render
from django.views import View

from staff.models.certificate import Certificate

class DetailView(View):
    def get(self, request, certificate_credential):
        certificate = Certificate.objects.filter(credential=certificate_credential).first()

        if not certificate:
            return render(
                request,
                'certificate/error.html',
                {
                    'certificate_credential': certificate_credential
                }
            )

        return render(
            request,
            'certificate/detail.html',
            {
                'certificate': certificate
            }
        )
