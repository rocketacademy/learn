from django.contrib import admin

# Register your models here.
from .models import Batch, Course, Section, BatchSchedule

class SectionAdmin(admin.ModelAdmin):
    list_display = ("number", "batch")

class BatchAdmin(admin.ModelAdmin):
    list_display = ("course", "number", "start_date", "end_date", "capacity", "sections")

class BatchScheduleAdmin(admin.ModelAdmin):
    list_display = ("batch", "course_day", "start_time", "end_time", "deleted_at")


# Register your models here.
admin.site.register(Batch, BatchAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Course)
admin.site.register(BatchSchedule, BatchScheduleAdmin)

