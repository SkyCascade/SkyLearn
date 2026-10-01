from django.apps import AppConfig


class GamificationConfig(AppConfig):
    name = "gamification"
    verbose_name = "Gamification"

    def ready(self):
        from django.db.models.signals import post_migrate
        from .signals import seed_gamification_defaults
        post_migrate.connect(seed_gamification_defaults, sender=self)