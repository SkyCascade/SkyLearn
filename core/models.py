from django.db import models
from django.utils.translation import gettext_lazy as _

from config import settings


class Course(models.Model):
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_courses',
        limit_choices_to={'is_superuser': True},
        null=True,
        blank=True
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Courses"

    def __str__(self):
        return f"{self.name}"


class CourseAllocation(models.Model):
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_course_allocations',
        limit_choices_to={'is_superuser': True},
        null=True,
        blank=True
    )
    lecturer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='course_allocations',
        limit_choices_to={'is_lecturer': True}
    )
    courses = models.ManyToManyField(Course, related_name='course_allocations')
    semester = models.ForeignKey('core.Semester', on_delete=models.CASCADE, related_name='course_allocations')
    group = models.ForeignKey('accounts.Group', on_delete=models.CASCADE, related_name='course_allocations')

    class Meta:
        verbose_name = "Course Allocation"
        verbose_name_plural = "Course Allocations"

    def __str__(self):
        return f"{self.lecturer.username} - {self.semester} - {self.group.name}"

class SemesterName(models.TextChoices):
    FIRST = "First", _("First")
    SECOND = "Second", _("Second")

# preserve old export name for serializers and other modules
SEMESTER = SemesterName.choices


class Program(models.Model):
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, 
        related_name='created_programs',
        limit_choices_to={'is_superuser': True},
        null=True,
        blank=True
    )
    name = models.CharField(max_length=200)


    class Meta:
        verbose_name = "Program"
        verbose_name_plural = "Programs"

    def __str__(self):
        return self.name


class AcademicYear(models.Model):
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='created_academic_years',
        limit_choices_to={'is_superuser': True},
        null=True,
        blank=True
    )
    year = models.IntegerField(unique=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="academic_years")
    is_current = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.year} - {self.program.name}"


class Semester(models.Model):
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='created_semesters',
        limit_choices_to={'is_superuser': True},
        null=True,
        blank=True
    )
    name = models.CharField(max_length=10, choices=SemesterName.choices, default=SemesterName.FIRST)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='semesters')
    courses = models.ManyToManyField(Course,  related_name='semesters')
    is_current = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.academic_year}"
    
    class Meta:
        verbose_name = "Semester"
        verbose_name_plural = "Semesters"

class Module(models.Model):
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_modules',
        limit_choices_to={'is_superuser': True},
        null=True,
        blank=True
    )
    name = models.CharField(max_length=10, choices=SemesterName.choices)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='modules')
    is_current = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.semester}"

    class Meta:
        verbose_name = "Module"
        verbose_name_plural = "Modules"
