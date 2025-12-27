from django.urls import path
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()


urlpatterns = [

    path('api/', include(router.urls)),

    # Semester urls
    path('api/semesters/', views.SemesterListAPIView.as_view(), name='semester-list'),
    path('api/semesters/create/', views.SemesterCreateAPIView.as_view(), name='semester-create'),
    path('api/semesters/<int:pk>/update/', views.SemesterUpdateAPIView.as_view(), name='semester-update'),
    path('api/semesters/<int:pk>/', views.SemesterRetrieveDestroyAPIView.as_view(), name='semester-detail'),

    # Program urls
    path('api/programs/', views.ProgramListAPIView.as_view(), name='program-list'),
    path('api/programs/create/', views.ProgramCreateAPIView.as_view(), name='program-create'),
    path('api/programs/<int:pk>/update/', views.ProgramUpdateAPIView.as_view(), name='program-update'),
    path('api/programs/<int:pk>/', views.ProgramRetrieveDestroyAPIView.as_view(), name='program-detail'),

    # Academic Year urls
    path('api/academic-years/', views.AcademicYearListAPIView.as_view(), name='academic-year-list'),
    path('api/academic-years/create/', views.AcademicYearCreateAPIView.as_view(), name='academic-year-create'),
    path('api/academic-years/<int:pk>/update/', views.AcademicYearUpdateAPIView.as_view(), name='academic-year-update'),
    path('api/academic-years/<int:pk>/', views.AcademicYearRetrieveDestroyAPIView.as_view(), name='academic-year-detail'),

    # Module urls
    path('api/modules/', views.ModuleListAPIView.as_view(), name='module-list'),
    path('api/modules/create/', views.ModuleCreateAPIView.as_view(), name='module-create'),
    path('api/modules/<int:pk>/update/', views.ModuleUpdateAPIView.as_view(), name='module-update'),
    path('api/modules/<int:pk>/', views.ModuleRetrieveDestroyAPIView.as_view(), name='module-detail'),
 
]
