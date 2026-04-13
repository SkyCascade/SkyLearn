from django.contrib import admin

from .models import Attendance, ScheduleItem

admin.site.register(ScheduleItem)
admin.site.register(Attendance)
