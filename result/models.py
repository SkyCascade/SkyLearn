from decimal import Decimal
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps

A_PLUS = "A+"
A = "A"
A_MINUS = "A-"
B_PLUS = "B+"
B = "B"
B_MINUS = "B-"
C_PLUS = "C+"
C = "C"
C_MINUS = "C-"
D = "D"
F = "F"
NG = "NG"

GRADE_CHOICES = (
    (A_PLUS, "A+"),
    (A, "A"),
    (A_MINUS, "A-"),
    (B_PLUS, "B+"),
    (B, "B"),
    (B_MINUS, "B-"),
    (C_PLUS, "C+"),
    (C, "C"),
    (C_MINUS, "C-"),
    (D, "D"),
    (F, "F"),
    (NG, "NG"),
)

PASS = "PASS"
FAIL = "FAIL"

COMMENT_CHOICES = (
    (PASS, "PASS"),
    (FAIL, "FAIL"),
)

GRADE_BOUNDARIES = [
    (90, A_PLUS),
    (85, A),
    (80, A_MINUS),
    (75, B_PLUS),
    (70, B),
    (65, B_MINUS),
    (60, C_PLUS),
    (55, C),
    (50, C_MINUS),
    (45, D),
    (0, F),
]





class Grade_1st_module(models.Model):
    lecturer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="grade_1st_lecturer",
    )
    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE)
    course = models.ForeignKey('course.Course', on_delete=models.CASCADE, related_name="grade_1st_courses")
    attendance = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    activities = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    exam = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, blank=True, null=True)

    class Meta:
        unique_together = ['student', 'course']

    def __str__(self):
        return f"{self.student} - {self.course} (1st Module)"

class Grade_2nd_module(models.Model):
    lecturer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="grade_2nd_lecturer",
    )
    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE)
    course = models.ForeignKey('course.Course', on_delete=models.CASCADE, related_name="grade_2nd_courses")
    attendance = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    activities = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    exam = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, blank=True, null=True)

    class Meta:
        unique_together = ['student', 'course']

    def __str__(self):
        return f"{self.student} - {self.course} (2nd Module)"

class Grade_semester(models.Model):
    lecturer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="grade_semester_lecturer",
    )
    semester = models.ForeignKey(
        "core.Semester", on_delete=models.CASCADE, blank=True, null=True
    )
    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE)
    course = models.ForeignKey('course.Course', on_delete=models.CASCADE, related_name="grade_semester_courses")
    attendance = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    activities = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    exam = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, blank=True, null=True)

    class Meta:
        unique_together = ['student', 'course', 'semester']

    def __str__(self):
        return f"{self.student} - {self.course} (Semester)"