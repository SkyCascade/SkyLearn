from django.contrib import admin
from django.contrib.auth.models import Group

from .models import Grade_1st_module, Grade_2nd_module, Grade_semester



admin.site.register(Grade_1st_module)
admin.site.register(Grade_2nd_module)
admin.site.register(Grade_semester) 