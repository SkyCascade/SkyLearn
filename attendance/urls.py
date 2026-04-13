from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AttendanceViewSet, LessonTimeViewSet, ScheduleItemViewSet

router = DefaultRouter()
router.register(r"lesson-times", LessonTimeViewSet, basename="lesson-time")
router.register(r"schedules", ScheduleItemViewSet, basename="schedule")
router.register(r"attendances", AttendanceViewSet, basename="attendance")

app_name = "attendance"

urlpatterns = [
    path("", include(router.urls)),
]
