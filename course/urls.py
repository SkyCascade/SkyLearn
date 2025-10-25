from django.urls import path, include
from . import views
from .views import ProgramListAPIView, ProgramDetailAPIView, CourseListCreateAPIView, CourseDetailAPIView , CourseAllocationViewSet, StudentCoursesListAPIView
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'course-allocations', CourseAllocationViewSet, basename='courseallocation')

urlpatterns = [
    # Program urls
    path('api/<int:pk>/', ProgramDetailAPIView.as_view(), name='program-detail'),
    path('api/', ProgramListAPIView.as_view(), name='program-list'),
    path('api/course/<int:pk>/', CourseDetailAPIView.as_view(), name='course-detail'),
    path('api/course/', CourseListCreateAPIView.as_view(), name='course-list-create'), 
    path('api/student-courses/',  StudentCoursesListAPIView.as_view(),  name='student-courses'),
    path('api/teacher-allocations/', views.CourseAllocationViewSet.as_view({'get': 'my_allocations'}), name='my-allocations'),
    path('', include(router.urls)),

]
