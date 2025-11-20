from django.urls import path
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'news', views.NewsAndEventsViewSet, basename='news')
router.register(r'semesters', views.SemesterViewSet, basename='semester')


urlpatterns = [

      
    path('api/', include(router.urls)),

    # Accounts url
 
]
