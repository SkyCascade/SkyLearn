from django.conf import settings
from django.db import models

from course.models import Course


class LectureSlot(models.Model):
    """
    A recurring weekly timetable slot for a course (e.g. "Monday 10:00
    Lecture"). This does NOT represent an actual lecture that happened —
    AttendanceSession does that. A slot just lets a lecturer quickly create
    today's session from the right recurring slot instead of typing the
    time in every time.
    """

    MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY = range(7)
    DAY_CHOICES = (
        (MONDAY, "Monday"),
        (TUESDAY, "Tuesday"),
        (WEDNESDAY, "Wednesday"),
        (THURSDAY, "Thursday"),
        (FRIDAY, "Friday"),
        (SATURDAY, "Saturday"),
        (SUNDAY, "Sunday"),
    )

    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="lecture_slots"
    )
    label = models.CharField(
        max_length=100, blank=True,
        help_text="e.g. 'Lecture', 'Lab' — optional, shown alongside the day/time.",
    )
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("day_of_week", "start_time")

    def __str__(self):
        return f"{self.course.code} - {self.get_day_of_week_display()} {self.start_time} {self.label}".strip()


class AttendanceSession(models.Model):
    """
    One actual occurrence of a lecture on a specific date. Created either
    from a LectureSlot (fast path) or manually by the lecturer for an
    ad-hoc session with no fixed slot.
    """

    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="attendance_sessions"
    )
    lecture_slot = models.ForeignKey(
        LectureSlot, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="sessions",
    )
    date = models.DateField()
    topic = models.CharField(max_length=200, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-date", "-created_at")
        unique_together = ("course", "date", "lecture_slot")

    def __str__(self):
        return f"{self.course.code} - {self.date}"


class AttendanceRecord(models.Model):
    PRESENT = "present"
    ABSENT = "absent"
    STATUS_CHOICES = (
        (PRESENT, "Present"),
        (ABSENT, "Absent"),
    )

    session = models.ForeignKey(
        AttendanceSession, on_delete=models.CASCADE, related_name="records"
    )
    student = models.ForeignKey(
        "accounts.Student", on_delete=models.CASCADE, related_name="attendance_records"
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=ABSENT)
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    marked_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("session", "student")

    def __str__(self):
        return f"{self.student} - {self.session} - {self.status}"