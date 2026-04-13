from django.conf import settings
from django.db import models

from accounts.models import Group, Student
from core.models import Course

# Create your models here.

Days = (
    ("Monday", "Monday"),
    ("Tuesday", "Tuesday"),
    ("Wednesday", "Wednesday"),
    ("Thursday", "Thursday"),
    ("Friday", "Friday"),
)


class LessonTime(models.Model):
    """
    Модель для хранения типовых времен уроков
    Например: 1-й урок 9:00-10:30, 2-й урок 10:40-12:10 и т.д.
    """

    order = models.IntegerField(unique=True, help_text="Номер урока (1, 2, 3, ...)")
    start_time = models.TimeField(help_text="Время начала урока")
    end_time = models.TimeField(help_text="Время окончания урока")
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lesson_times",
        limit_choices_to={"is_superuser": True},
        null=True,
        blank=True,
        help_text="Администратор, создавший это расписание времен",
    )

    class Meta:
        ordering = ["order"]
        verbose_name = "Lesson Time"
        verbose_name_plural = "Lesson Times"
        unique_together = [["order", "admin"]]

    def __str__(self):
        return f"Урок {self.order}: {self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"


class ScheduleItem(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    lesson_time = models.ForeignKey(
        LessonTime,
        on_delete=models.CASCADE,
        help_text="Время урока (автоматически определяет start и end)",
        null=True,
        blank=True,
    )
    day = models.CharField(choices=Days, max_length=10)
    date = models.DateField(help_text="Дата проведения урока", null=True, blank=True)
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_schedule_items",
        limit_choices_to={"is_superuser": True},
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["date", "lesson_time__order"]
        verbose_name = "Schedule Item"
        verbose_name_plural = "Schedule Items"

    def __str__(self):
        return (
            f"{self.course.title} - {self.group.name} - {self.day} ({self.lesson_time})"
        )

    @property
    def start_time(self):
        """Время начала урока из LessonTime"""
        return self.lesson_time.start_time if self.lesson_time else self.start

    @property
    def end_time(self):
        """Время окончания урока из LessonTime"""
        return self.lesson_time.end_time if self.lesson_time else self.end

    @property
    def lesson_order(self):
        """Номер урока"""
        return self.lesson_time.order if self.lesson_time else self.order


class Attendance(models.Model):
    Student = models.ForeignKey(Student, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    shcedule = models.ForeignKey(ScheduleItem, on_delete=models.CASCADE)
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_attendances",
        limit_choices_to={"is_superuser": True},
        null=True,
        blank=True,
    )
