# result/apps.py
from django.apps import AppConfig


class ResultConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "result"

    def ready(self):
        import result.signals  # noqa: F401  # registers signal handlers
