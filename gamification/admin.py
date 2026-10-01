from django.contrib import admin
from .models import (
    Badge, GamificationSettings, LearningStreak, QuizXPRecord,
    StudentBadge, StudentXP, XPHistory, XPRule,
)


@admin.register(XPRule)
class XPRuleAdmin(admin.ModelAdmin):
    list_display = ("action", "xp_amount", "is_active")
    list_editable = ("xp_amount", "is_active")


@admin.register(StudentXP)
class StudentXPAdmin(admin.ModelAdmin):
    list_display = ("student", "total_xp", "updated_at")
    search_fields = ("student__username", "student__first_name", "student__last_name")
    readonly_fields = ("total_xp",)  # only award_xp() should change this, never a raw admin edit


@admin.register(XPHistory)
class XPHistoryAdmin(admin.ModelAdmin):
    list_display = ("student", "action", "xp_amount", "created_at")
    list_filter = ("action",)
    search_fields = ("student__username",)
    date_hierarchy = "created_at"


class StudentBadgeInline(admin.TabularInline):
    model = StudentBadge
    extra = 0
    readonly_fields = ("student", "earned_at")
    can_delete = False


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ("name", "criteria_type", "criteria_value", "is_active")
    list_editable = ("is_active",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = [StudentBadgeInline]


@admin.register(LearningStreak)
class LearningStreakAdmin(admin.ModelAdmin):
    list_display = ("student", "current_streak", "longest_streak", "total_active_days", "last_activity_date")
    search_fields = ("student__username",)


@admin.register(QuizXPRecord)
class QuizXPRecordAdmin(admin.ModelAdmin):
    list_display = ("student", "quiz", "best_percent", "attempts_recorded", "last_attempt_at")
    search_fields = ("student__username", "quiz__title")


@admin.register(GamificationSettings)
class GamificationSettingsAdmin(admin.ModelAdmin):
    list_display = ("leaderboard_enabled",)

    def has_add_permission(self, request):
        return not GamificationSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False