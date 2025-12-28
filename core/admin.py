from django.contrib import admin
from .models import Semester, Program, AcademicYear, Module, CourseAllocation, Course



admin.site.register(Semester)
admin.site.register(Program)
admin.site.register(AcademicYear)
admin.site.register(Module)
admin.site.register(Course)
admin.site.register(CourseAllocation)
