from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomTokenObtainPairView,
    SecureTokenRefreshView,
    LogoutView,
    UserProfileView,
    StudentProfileView,
    UserDetailUpdateView,
    StudentListView,
    LecturerListViewSet,
    GroupViewSet,
    StudentUpdateView,
    StudentDetailView,
    StudentsByGroupView,
    StaffCreateView,
    StudentCreateView,
    ChangePasswordView,
)

router = DefaultRouter()
router.register(r'groups', GroupViewSet, basename='group')

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', SecureTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('profile/student/', StudentProfileView.as_view(), name='student_profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('create-staff/', StaffCreateView.as_view(), name='create-staff'),
    path('create-student/', StudentCreateView.as_view(), name='create-student'),
    path('users/<int:pk>/', UserDetailUpdateView.as_view(), name='user-detail-update'),
    path('api/lecturers/', LecturerListViewSet.as_view({'get': 'list'}), name='lecturer-list'),
    path('api/students/', StudentListView.as_view(), name='student-list'),
    path('api/student/<int:pk>/', StudentDetailView.as_view(), name='student-detail'),
    path('api/student-update/<int:pk>/', StudentUpdateView.as_view(), name='student-update'),
    path('api/groups/<slug:group_name>/students', StudentsByGroupView.as_view(), name='students-by-group'),
    path("api/", include(router.urls)),
]
