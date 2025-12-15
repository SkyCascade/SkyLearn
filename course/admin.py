from django.contrib import admin
from django.contrib.auth.models import Group

from .models import Program, Course, CourseAllocation, Upload, Enrollment
from modeltranslation.admin import TranslationAdmin

class ProgramAdmin(TranslationAdmin):
    pass
class CourseAdmin(TranslationAdmin):
    pass
class UploadAdmin(TranslationAdmin):
    pass
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_on')
    list_filter = ('course',)

admin.site.register(Program, ProgramAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(CourseAllocation)
admin.site.register(Upload, UploadAdmin)
