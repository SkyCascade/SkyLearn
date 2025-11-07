from django.db import models
from accounts.models import Student
from accounts.models import Group
from course.models import Course


# Create your models here.

Days = (
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
)

class ScheduleItem(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    order = models.IntegerField()
    day = models.CharField(choices=Days, max_length=10)
    start = models.TimeField()
    end = models.TimeField()


class Attendance(models.Model):
    Student = models.ForeignKey(Student, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    shcedule = models.ForeignKey(ScheduleItem, on_delete=models.CASCADE)



 