from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import ProgramCycle, Cohort, NewsAndEvents


class NewsAndEventsAdmin(TranslationAdmin):
    pass


admin.site.register(Cohort)
admin.site.register(ProgramCycle)
admin.site.register(NewsAndEvents, NewsAndEventsAdmin)
