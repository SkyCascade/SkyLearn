from django.contrib import admin

from .models import AcademicYear, Course, CourseAllocation, Module, Program, Semester

admin.site.register(Semester)
admin.site.register(Program)
admin.site.register(AcademicYear)
admin.site.register(Module)
admin.site.register(Course)
admin.site.register(CourseAllocation)
