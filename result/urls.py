from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    Grade1stModuleViewSet,
    Grade2ndModuleViewSet,
    GradeSemesterViewSet,
    LecturerBulkGradesViewSet,
    LecturerCourseGradesViewSet
)

router = DefaultRouter()
router.register(r'grade-1st-modules', Grade1stModuleViewSet, basename='grade-1st-modules')
router.register(r'grade-2nd-modules', Grade2ndModuleViewSet, basename='grade-2nd-modules')
router.register(r'grade-semesters', GradeSemesterViewSet, basename='grade-semesters')
router.register(r'lecturer/bulk-grades', LecturerBulkGradesViewSet, basename='lecturer-bulk-grades')
router.register(r'lecturer/course-grades', LecturerCourseGradesViewSet, basename='lecturer-course-grades')

urlpatterns = [
    path('api/', include(router.urls)),
]