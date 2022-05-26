from django.contrib import admin

from .models.registration import Registration
from .models.enrolment import Enrolment

admin.site.register(Registration)
admin.site.register(Enrolment)
