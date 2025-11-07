from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ScheduleItemViewSet, AttendanceViewSet

router = DefaultRouter()
router.register(r'schedules', ScheduleItemViewSet, basename='schedule')
router.register(r'attendances', AttendanceViewSet, basename='attendance')

app_name = 'attendance'

urlpatterns = [
    path('', include(router.urls)),
]
