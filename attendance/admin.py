from django.contrib import admin
from .models import ScheduleItem, Attendance


@admin.register(ScheduleItem)
class ScheduleItemAdmin(admin.ModelAdmin):
    list_display = ['course', 'group', 'day', 'start', 'end', 'order']
    list_filter = ['day', 'course', 'group']
    search_fields = ['course__title', 'course__code', 'group__name']
    ordering = ['day', 'start', 'order']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('course', 'group', 'day', 'order')
        }),
        ('Время', {
            'fields': ('start', 'end')
        }),
    )


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['get_student_name', 'get_course', 'get_schedule_day', 'get_schedule_time', 'status']
    list_filter = ['status', 'shcedule__day', 'shcedule__course']
    search_fields = ['Student__student__first_name', 'Student__student__last_name', 'shcedule__course__title']
    raw_id_fields = ['Student', 'shcedule']
    
    fieldsets = (
        ('Информация о посещаемости', {
            'fields': ('Student', 'shcedule', 'status')
        }),
    )
    
    def get_student_name(self, obj):
        return obj.Student.get_full_name()
    get_student_name.short_description = 'Студент'
    get_student_name.admin_order_field = 'Student__student__first_name'
    
    def get_course(self, obj):
        return obj.shcedule.course.title if obj.shcedule else '-'
    get_course.short_description = 'Курс'
    get_course.admin_order_field = 'shcedule__course__title'
    
    def get_schedule_day(self, obj):
        return obj.shcedule.day if obj.shcedule else '-'
    get_schedule_day.short_description = 'День'
    get_schedule_day.admin_order_field = 'shcedule__day'
    
    def get_schedule_time(self, obj):
        if obj.shcedule:
            return f"{obj.shcedule.start.strftime('%H:%M')} - {obj.shcedule.end.strftime('%H:%M')}"
        return '-'
    get_schedule_time.short_description = 'Время'
