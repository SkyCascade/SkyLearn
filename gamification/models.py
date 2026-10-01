from django.conf import settings
from django.db import models


class XPRule(models.Model):
    """Centralized, admin-editable XP values — nothing is hard-coded elsewhere."""

    VIDEO_COMPLETE = "video_complete"
    MODULE_COMPLETE = "module_complete"       # unused until a Module/Lesson model exists
    COURSE_COMPLETE = "course_complete"
    QUIZ_FIRST_COMPLETE = "quiz_first_complete"
    QUIZ_PERFECT_SCORE = "quiz_perfect_score"
    QUIZ_IMPROVEMENT = "quiz_improvement"
    STREAK_MILESTONE = "streak_milestone"

    ACTION_CHOICES = (
        (VIDEO_COMPLETE, "Video completed"),
        (MODULE_COMPLETE, "Module/lesson completed"),
        (COURSE_COMPLETE, "Course completed"),
        (QUIZ_FIRST_COMPLETE, "Quiz completed (first attempt)"),
        (QUIZ_PERFECT_SCORE, "Quiz perfect score bonus"),
        (QUIZ_IMPROVEMENT, "Quiz score improved"),
        (STREAK_MILESTONE, "Weekly streak milestone"),
    )

    DEFAULT_AMOUNTS = {
        VIDEO_COMPLETE: 20,
        MODULE_COMPLETE: 50,
        COURSE_COMPLETE: 200,
        QUIZ_FIRST_COMPLETE: 10,
        QUIZ_PERFECT_SCORE: 15,
        QUIZ_IMPROVEMENT: 20,
        STREAK_MILESTONE: 10,
    }

    action = models.CharField(max_length=32, choices=ACTION_CHOICES, unique=True)
    xp_amount = models.PositiveIntegerField()
    is_active = models.BooleanField(
        default=True,
        help_text="Untick to stop awarding XP for this action without deleting history.",
    )

    def __str__(self):
        return f"{self.get_action_display()}: {self.xp_amount} XP"


class StudentXP(models.Model):
    student = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="gamification_xp"
    )
    total_xp = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student} - {self.total_xp} XP"


class XPHistory(models.Model):
    """Full audit trail — every XP award, ever, with a reason."""

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="xp_history"
    )
    action = models.CharField(max_length=32, choices=XPRule.ACTION_CHOICES)
    xp_amount = models.PositiveIntegerField()
    reason = models.CharField(max_length=200)

    related_video = models.ForeignKey(
        "course.UploadVideo", on_delete=models.SET_NULL, null=True, blank=True
    )
    related_course = models.ForeignKey(
        "course.Course", on_delete=models.SET_NULL, null=True, blank=True
    )
    related_quiz = models.ForeignKey(
        "quiz.Quiz", on_delete=models.SET_NULL, null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name_plural = "XP history"

    def __str__(self):
        return f"{self.student} +{self.xp_amount} XP ({self.get_action_display()})"


class Badge(models.Model):
    VIDEOS_COMPLETED = "videos_completed"
    QUIZ_PERFECT_COUNT = "quiz_perfect_count"
    QUIZ_HIGH_SCORE_COUNT = "quiz_high_score_count"
    STREAK_DAYS = "streak_days"
    COURSE_COMPLETED_COUNT = "course_completed_count"
    ACTIVE_DAYS = "active_days"
    QUIZ_COMEBACK = "quiz_comeback"

    CRITERIA_CHOICES = (
        (VIDEOS_COMPLETED, "Number of videos completed"),
        (QUIZ_PERFECT_COUNT, "Number of perfect quiz scores"),
        (QUIZ_HIGH_SCORE_COUNT, "Number of high (80%+) quiz scores"),
        (STREAK_DAYS, "Current streak length (days)"),
        (COURSE_COMPLETED_COUNT, "Number of courses fully completed"),
        (ACTIVE_DAYS, "Total distinct days with learning activity"),
        (QUIZ_COMEBACK, "At least one big quiz score improvement"),
    )

    DEFAULT_BADGES = [
        dict(name="Video Explorer", slug="video-explorer", description="Complete 5 videos.",
             icon_class="fa-solid fa-compass", criteria_type=VIDEOS_COMPLETED, criteria_value=5),
        dict(name="Video Master", slug="video-master", description="Complete 20 videos.",
             icon_class="fa-solid fa-crown", criteria_type=VIDEOS_COMPLETED, criteria_value=20),
        dict(name="Quiz Master", slug="quiz-master", description="Score 80%+ on 5 quizzes.",
             icon_class="fa-solid fa-brain", criteria_type=QUIZ_HIGH_SCORE_COUNT, criteria_value=5),
        dict(name="Perfect Score", slug="perfect-score", description="Get 100% on a quiz.",
             icon_class="fa-solid fa-bullseye", criteria_type=QUIZ_PERFECT_COUNT, criteria_value=1),
        dict(name="7-Day Streak", slug="7-day-streak", description="Learn 7 days in a row.",
             icon_class="fa-solid fa-fire", criteria_type=STREAK_DAYS, criteria_value=7),
        dict(name="14-Day Streak", slug="14-day-streak", description="Learn 14 days in a row.",
             icon_class="fa-solid fa-fire", criteria_type=STREAK_DAYS, criteria_value=14),
        dict(name="Course Champion", slug="course-champion", description="Complete an entire course.",
             icon_class="fa-solid fa-trophy", criteria_type=COURSE_COMPLETED_COUNT, criteria_value=1),
        dict(name="Consistent Learner", slug="consistent-learner", description="Stay active for 30 days.",
             icon_class="fa-solid fa-calendar-check", criteria_type=ACTIVE_DAYS, criteria_value=30),
        dict(name="Comeback Learner", slug="comeback-learner", description="Significantly improve a quiz score.",
             icon_class="fa-solid fa-chart-line", criteria_type=QUIZ_COMEBACK, criteria_value=1),
    ]

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.CharField(max_length=200)
    icon_class = models.CharField(max_length=50, default="fa-solid fa-award")
    icon_image = models.ImageField(upload_to="badges/", blank=True, null=True)
    criteria_type = models.CharField(max_length=32, choices=CRITERIA_CHOICES)
    criteria_value = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("criteria_type", "criteria_value")

    def __str__(self):
        return self.name


class StudentBadge(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="badges"
    )
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name="awarded_to")
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "badge")
        ordering = ("-earned_at",)

    def __str__(self):
        return f"{self.student} earned {self.badge}"


class LearningStreak(models.Model):
    student = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="learning_streak"
    )
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    total_active_days = models.PositiveIntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.student} - {self.current_streak} day streak"


class QuizXPRecord(models.Model):
    """
    Gamification's own memory of quiz attempts, needed because quiz.Sitting
    is deleted by the quiz app itself once a non-exam-paper quiz completes.
    """

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quiz_xp_records"
    )
    quiz = models.ForeignKey("quiz.Quiz", on_delete=models.CASCADE, related_name="xp_records")

    best_percent = models.FloatField(default=0)
    attempts_recorded = models.PositiveIntegerField(default=0)
    achieved_big_comeback = models.BooleanField(default=False)
    last_attempt_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("student", "quiz")

    def __str__(self):
        return f"{self.student} / {self.quiz} - best {self.best_percent:.0f}%"


class GamificationSettings(models.Model):
    leaderboard_enabled = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Gamification settings"