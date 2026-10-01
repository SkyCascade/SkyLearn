from django.contrib import admin

from .models import AttendanceRecord, AttendanceSession, LectureSlot


@admin.register(LectureSlot)
class LectureSlotAdmin(admin.ModelAdmin):
    list_display = ("course", "day_of_week", "start_time", "label", "is_active")
    list_filter = ("course", "day_of_week", "is_active")


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ("course", "date", "lecture_slot", "topic", "created_by")
    list_filter = ("course", "date")


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ("session", "student", "status", "marked_by", "marked_at")
    list_filter = ("status", "session__course")