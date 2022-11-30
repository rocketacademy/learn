from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from urllib.parse import urlencode

from staff.models.certificate import Certificate

class BasicsCertificateDetailView(View):
    # Deprecated for the more generic DetailView
    # Must be left here as some students already have links to their certificates at this route
    def get(self, request, certificate_credential):
        return redirect(reverse('certificate_detail', kwargs={'certificate_credential': certificate_credential}))

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
