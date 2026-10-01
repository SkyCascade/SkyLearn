from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .models import (
    Badge, GamificationSettings, LearningStreak, QuizXPRecord,
    StudentBadge, StudentXP, XPHistory, XPRule,
)

LEVEL_THRESHOLDS = [
    (0, 1, "Newcomer"),
    (101, 2, "Learner"),
    (301, 3, "Achiever"),
    (601, 4, "Scholar"),
    (1001, 5, "Expert"),
    (2001, 6, "Master"),
]

QUIZ_IMPROVEMENT_MIN_DELTA = 10
QUIZ_COMEBACK_MIN_DELTA = 25
QUIZ_HIGH_SCORE_THRESHOLD = 80


def get_level_info(total_xp):
    current = LEVEL_THRESHOLDS[0]
    next_threshold = None
    for i, entry in enumerate(LEVEL_THRESHOLDS):
        if total_xp >= entry[0]:
            current = entry
            next_threshold = LEVEL_THRESHOLDS[i + 1] if i + 1 < len(LEVEL_THRESHOLDS) else None
        else:
            break

    level_start_xp, level_number, level_name = current
    if next_threshold:
        span = next_threshold[0] - level_start_xp
        progress_percent = round(min((total_xp - level_start_xp) / span, 1.0) * 100, 1) if span else 100
        next_level_xp = next_threshold[0]
    else:
        progress_percent, next_level_xp = 100, None

    return {
        "level": level_number, "level_name": level_name, "total_xp": total_xp,
        "next_level_xp": next_level_xp, "progress_percent": progress_percent,
    }


def _get_xp_amount(action):
    rule = XPRule.objects.filter(action=action, is_active=True).first()
    return rule.xp_amount if rule else XPRule.DEFAULT_AMOUNTS.get(action, 0)


@transaction.atomic
def award_xp(student, action, reason, related_video=None, related_course=None, related_quiz=None):
    amount = _get_xp_amount(action)
    if amount <= 0:
        return None

    totals, _ = StudentXP.objects.get_or_create(student=student)
    totals.total_xp += amount
    totals.save(update_fields=["total_xp", "updated_at"])

    return XPHistory.objects.create(
        student=student, action=action, xp_amount=amount, reason=reason,
        related_video=related_video, related_course=related_course, related_quiz=related_quiz,
    )


@transaction.atomic
def record_qualifying_activity(student, activity_date=None):
    """Idempotent per calendar day — safe to call more than once on the same day."""
    activity_date = activity_date or timezone.localdate()
    streak, _ = LearningStreak.objects.get_or_create(student=student)

    if streak.last_activity_date == activity_date:
        return streak

    if streak.last_activity_date == activity_date - timedelta(days=1):
        streak.current_streak += 1
    else:
        streak.current_streak = 1

    streak.longest_streak = max(streak.longest_streak, streak.current_streak)
    streak.total_active_days += 1
    streak.last_activity_date = activity_date
    streak.save()

    if streak.current_streak % 7 == 0:
        award_xp(student, XPRule.STREAK_MILESTONE, reason=f"{streak.current_streak}-day learning streak")

    return streak


def _videos_completed_count(student):
    from course.models import VideoProgress
    return VideoProgress.objects.filter(student=student, completed=True).count()


def _is_course_completed(student, course):
    from course.models import UploadVideo, VideoProgress
    video_ids = list(UploadVideo.objects.filter(course=course).values_list("id", flat=True))
    if not video_ids:
        return False
    completed_ids = set(
        VideoProgress.objects.filter(student=student, video_id__in=video_ids, completed=True)
        .values_list("video_id", flat=True)
    )
    return set(video_ids) == completed_ids


def _courses_completed_count(student):
    from course.models import Course
    from result.models import TakenCourse

    profile = getattr(student, "student", None)
    if profile is None:
        return 0
    course_ids = TakenCourse.objects.filter(student=profile).values_list("course_id", flat=True)
    return sum(1 for c in Course.objects.filter(id__in=course_ids) if _is_course_completed(student, c))


@transaction.atomic
def check_and_award_badges(student):
    already = set(StudentBadge.objects.filter(student=student).values_list("badge_id", flat=True))
    candidates = Badge.objects.filter(is_active=True).exclude(id__in=already)
    if not candidates:
        return []

    streak = LearningStreak.objects.filter(student=student).first()
    newly_awarded = []

    for badge in candidates:
        if badge.criteria_type == Badge.VIDEOS_COMPLETED:
            earned = _videos_completed_count(student) >= badge.criteria_value
        elif badge.criteria_type == Badge.QUIZ_PERFECT_COUNT:
            earned = QuizXPRecord.objects.filter(student=student, best_percent__gte=100).count() >= badge.criteria_value
        elif badge.criteria_type == Badge.QUIZ_HIGH_SCORE_COUNT:
            earned = QuizXPRecord.objects.filter(
                student=student, best_percent__gte=QUIZ_HIGH_SCORE_THRESHOLD
            ).count() >= badge.criteria_value
        elif badge.criteria_type == Badge.STREAK_DAYS:
            earned = bool(streak) and streak.current_streak >= badge.criteria_value
        elif badge.criteria_type == Badge.COURSE_COMPLETED_COUNT:
            earned = _courses_completed_count(student) >= badge.criteria_value
        elif badge.criteria_type == Badge.ACTIVE_DAYS:
            earned = bool(streak) and streak.total_active_days >= badge.criteria_value
        elif badge.criteria_type == Badge.QUIZ_COMEBACK:
            earned = QuizXPRecord.objects.filter(student=student, achieved_big_comeback=True).exists()
        else:
            earned = False

        if earned:
            StudentBadge.objects.get_or_create(student=student, badge=badge)
            newly_awarded.append(badge)

    return newly_awarded


@transaction.atomic
def award_video_completion(student, video):
    """Phase 4 hook target — called once, on the False→True transition only."""
    award_xp(student, XPRule.VIDEO_COMPLETE, reason=f'Completed "{video.title}"',
              related_video=video, related_course=video.course)
    record_qualifying_activity(student)
    newly_awarded = check_and_award_badges(student)

    if _is_course_completed(student, video.course):
        award_xp(student, XPRule.COURSE_COMPLETE, reason=f'Completed course "{video.course.title}"',
                  related_course=video.course)
        newly_awarded += check_and_award_badges(student)

    return newly_awarded


@transaction.atomic
def record_quiz_result(student, quiz, course, percent):
    """Phase 4 hook target — called from QuizTake.final_result_user."""
    record, created = QuizXPRecord.objects.get_or_create(student=student, quiz=quiz)

    if created or record.attempts_recorded == 0:
        award_xp(student, XPRule.QUIZ_FIRST_COMPLETE, reason=f'Completed quiz "{quiz.title}"',
                  related_quiz=quiz, related_course=course)
        if percent >= 100:
            award_xp(student, XPRule.QUIZ_PERFECT_SCORE, reason=f'Perfect score on "{quiz.title}"',
                      related_quiz=quiz, related_course=course)
    else:
        improvement = percent - record.best_percent
        if improvement >= QUIZ_IMPROVEMENT_MIN_DELTA:
            award_xp(student, XPRule.QUIZ_IMPROVEMENT,
                      reason=f'Improved "{quiz.title}" score by {improvement:.0f} points',
                      related_quiz=quiz, related_course=course)
        if improvement >= QUIZ_COMEBACK_MIN_DELTA:
            record.achieved_big_comeback = True
        if percent >= 100 and record.best_percent < 100:
            award_xp(student, XPRule.QUIZ_PERFECT_SCORE, reason=f'Perfect score on "{quiz.title}"',
                      related_quiz=quiz, related_course=course)

    record.best_percent = max(record.best_percent, percent)
    record.attempts_recorded += 1
    record.last_attempt_at = timezone.now()
    record.save()

    record_qualifying_activity(student)
    return check_and_award_badges(student)


def get_leaderboard(course=None, limit=10):
    if not GamificationSettings.load().leaderboard_enabled:
        return []

    qs = StudentXP.objects.select_related("student").order_by("-total_xp")
    if course is not None:
        from result.models import TakenCourse
        ids = TakenCourse.objects.filter(course=course).values_list("student__student_id", flat=True)
        qs = qs.filter(student_id__in=ids)

    return list(enumerate(qs[:limit], start=1))