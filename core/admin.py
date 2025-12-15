from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import Session, Semester, NewsAndEvents
from django.contrib import admin
from .models import AcademicCalendar

admin.site.register(AcademicCalendar)

class NewsAndEventsAdmin(TranslationAdmin):
    pass


admin.site.register(Semester)
admin.site.register(Session)
admin.site.register(NewsAndEvents, NewsAndEventsAdmin)
