import math

from .models import AttendanceRecord

DEFAULTER_THRESHOLD_PERCENT = 70


def get_attendance_stats(student, course):
    """
    student: an accounts.Student instance (the profile, not the User).
    course: a course.Course instance.

    Returns counts plus a "can I skip" projection. The projection assumes
    the course keeps adding sessions over time: max_more_skippable is how
    many additional lectures this student could miss (from today onward)
    while the running attendance percentage stays >= the threshold.
    """
    records = AttendanceRecord.objects.filter(
        student=student, session__course=course
    )

    total = records.count()
    attended = records.filter(status=AttendanceRecord.PRESENT).count()

    percent = round((attended / total) * 100, 1) if total else 100.0

    if total == 0:
        is_defaulter = False
        safe_to_skip_next = True
        max_more_skippable = None  # not enough data yet
    else:
        is_defaulter = percent < DEFAULTER_THRESHOLD_PERCENT
        safe_to_skip_next = (attended / (total + 1)) * 100 >= DEFAULTER_THRESHOLD_PERCENT
        max_more_skippable = max(
            0,
            math.floor(attended / (DEFAULTER_THRESHOLD_PERCENT / 100) - total),
        )

    return {
        "course": course,
        "total_sessions": total,
        "attended": attended,
        "absent": total - attended,
        "percent": percent,
        "is_defaulter": is_defaulter,
        "safe_to_skip_next": safe_to_skip_next,
        "max_more_skippable": max_more_skippable,
    }


def get_attendance_stats_for_courses(student, courses):
    return [get_attendance_stats(student, course) for course in courses]