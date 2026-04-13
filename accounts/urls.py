from django.urls import path

from .views import (
    CustomTokenObtainPairView,
    GroupCreateView,
    GroupListAPIView,
    GroupRetrieveUpdateDestroyView,
    LecturerCreateView,
    LecturerListAPIView,
    LecturerRetrieveDestroyView,
    LecturerUpdateView,
    ParentCreateView,
    ParentListAPIView,
    ParentRetrieveUpdateDestroyView,
    ParentUpdateView,
    SecureTokenRefreshView,
    StudentCreateView,
    StudentListAPIView,
    StudentListGroupAPIView,
    StudentRetrieveUpdateDestroyView,
    StudentUpdateAPIView,
    UserProfileView,
)

urlpatterns = [
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", SecureTokenRefreshView.as_view(), name="token_refresh"),
    path("profile/", UserProfileView.as_view(), name="user-profile"),
    # Lecturer URLs
    path("lecturers/", LecturerListAPIView.as_view(), name="lecturer-list"),
    path("lecturers/create/", LecturerCreateView.as_view(), name="lecturer-create"),
    path(
        "lecturers/<int:pk>/",
        LecturerRetrieveDestroyView.as_view(),
        name="lecturer-detail-delete",
    ),
    path(
        "lecturers/update/<int:pk>/",
        LecturerUpdateView.as_view(),
        name="lecturer-update",
    ),
    # Group URLs
    path("groups/", GroupListAPIView.as_view(), name="group-list"),
    path("groups/create/", GroupCreateView.as_view(), name="group-create"),
    path(
        "groups/<int:pk>/",
        GroupRetrieveUpdateDestroyView.as_view(),
        name="group-detail-delete",
    ),
    path(
        "groups/update/<int:pk>/",
        GroupRetrieveUpdateDestroyView.as_view(),
        name="group-update",
    ),
    # Parent URLs
    path("parents/", ParentListAPIView.as_view(), name="parent-list"),
    path("parents/create/", ParentCreateView.as_view(), name="parent-create"),
    path(
        "parents/<int:pk>/",
        ParentRetrieveUpdateDestroyView.as_view(),
        name="parent-detail-delete",
    ),
    path("parents/update/<int:pk>/", ParentUpdateView.as_view(), name="parent-update"),
    # Student URLs
    path("students/create/", StudentCreateView.as_view(), name="student-create"),
    path(
        "students/<int:pk>/",
        StudentRetrieveUpdateDestroyView.as_view(),
        name="student-detail-delete",
    ),
    path(
        "students/update/<int:pk>/",
        StudentUpdateAPIView.as_view(),
        name="student-update",
    ),
    path("students/", StudentListAPIView.as_view(), name="student-list"),
    path(
        "students/by-group/<int:group_id>/",
        StudentListGroupAPIView.as_view(),
        name="student-by-group",
    ),
]
