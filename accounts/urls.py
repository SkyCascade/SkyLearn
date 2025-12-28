from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomTokenObtainPairView,
    SecureTokenRefreshView,
    LecturerCreateView, 
    LecturerListAPIView,
    LecturerRetrieveUpdateDestroyView,
    StudentCreateView, 
    StudentListAPIView,
    StudentRetrieveUpdateDestroyView,
    GroupListAPIView,
    GroupCreateView,
    GroupRetrieveUpdateDestroyView,
    ParentCreateView,
    ParentListAPIView,
    ParentRetrieveUpdateDestroyView,
)


urlpatterns = [
    path('/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('/token/refresh/', SecureTokenRefreshView.as_view(), name='token_refresh'),
    # Lecturer URLs
    path('lecturers/', LecturerListAPIView.as_view(), name='lecturer-list'),
    path('lecturers/create/', LecturerCreateView.as_view(), name='lecturer-create'),
    path('lecturers/<int:pk>/', LecturerRetrieveUpdateDestroyView.as_view(), name='lecturer-detail'),
    path('lecturers/update/<int:pk>/', LecturerRetrieveUpdateDestroyView.as_view(), name='lecturer-update'),
    path('lecturers/delete/<int:pk>/', LecturerRetrieveUpdateDestroyView.as_view(), name='lecturer-delete'),
    # Group URLs
    path('groups/', GroupListAPIView.as_view(), name='group-list'),
    path('groups/create/', GroupCreateView.as_view(), name='group-create'),
    path('groups/<int:pk>/', GroupRetrieveUpdateDestroyView.as_view(), name='group-detail'),
    path('groups/update/<int:pk>/', GroupRetrieveUpdateDestroyView.as_view(), name='group-update'),
    path('groups/delete/<int:pk>/', GroupRetrieveUpdateDestroyView.as_view(), name='group-delete'),
    # Parent URLs
    path('parents/', ParentListAPIView.as_view(), name='parent-list'),
    path('parents/create/', ParentCreateView.as_view(), name='parent-create'),
    path('parents/<int:pk>/', ParentRetrieveUpdateDestroyView.as_view(), name='parent-detail'),
    path('parents/update/<int:pk>/', ParentRetrieveUpdateDestroyView.as_view(), name='parent-update'),
    path('parents/delete/<int:pk>/', ParentRetrieveUpdateDestroyView.as_view(), name='parent-delete'),
    # Student URLs
    path('students/create/', StudentCreateView.as_view(), name='student-create'),
    path('students/<int:pk>/', StudentRetrieveUpdateDestroyView.as_view(), name='student-detail'),
    path('students/update/<int:pk>/', StudentRetrieveUpdateDestroyView.as_view(), name='student-update'),
    path('students/delete/<int:pk>/', StudentRetrieveUpdateDestroyView.as_view(), name='student-delete'),
    path('students/', StudentListAPIView.as_view(), name='student-list'),
]
