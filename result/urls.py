# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TakenCourseViewSet, ResultViewSet

router = DefaultRouter()
router.register(r'taken-courses', TakenCourseViewSet)
router.register(r'results', ResultViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]