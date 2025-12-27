from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save, post_delete, post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _







class Course(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='created_courses',
        limit_choices_to={'is_superuser': True},
        null=True,
        blank=True
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("course_detail", kwargs={"slug": self.slug})



class CourseAllocation(models.Model):
    lecturer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="allocated_lecturer",
    )
    group = models.ForeignKey('accounts.Group', on_delete=models.CASCADE, null=True, blank=True)  

    courses = models.ManyToManyField(Course, related_name="allocated_course")
    semester = models.ForeignKey(
        "core.Semester", on_delete=models.CASCADE, blank=True, null=True
    )
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='created_course_allocations',
        limit_choices_to={'is_superuser': True},
        null=True,
        blank=True
    )

    def __str__(self):
        return self.lecturer.get_full_name

    def get_absolute_url(self):
        # Use the API detail URL instead
        return reverse("api-course-detail", kwargs={"slug": self.slug})
    

    def get_group_info(self):
        # Local import для методов, которые работают с Group
        from accounts.models import Group
        return f"Group: {self.group.name}" if self.group else "No group assigned"

    @classmethod
    def get_courses_by_group(cls, group_name):
        # Local import для class methods
        from accounts.models import Group
        try:
            group = Group.objects.get(name=group_name)
            return cls.objects.filter(group=group)
        except Group.DoesNotExist:
            return cls.objects.none()
