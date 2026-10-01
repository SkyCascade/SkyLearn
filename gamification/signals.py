from .models import Badge, GamificationSettings, XPRule


def seed_gamification_defaults(sender, **kwargs):
    if sender.name != "gamification":
        return
    for action, amount in XPRule.DEFAULT_AMOUNTS.items():
        XPRule.objects.get_or_create(action=action, defaults={"xp_amount": amount})
    for data in Badge.DEFAULT_BADGES:
        Badge.objects.get_or_create(slug=data["slug"], defaults=data)
    GamificationSettings.load()