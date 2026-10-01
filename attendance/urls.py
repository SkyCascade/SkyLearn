from django.urls import path

from . import views

urlpatterns = [
    path("", views.lecturer_home, name="attendance_lecturer_home"),
    path("<slug:slug>/sessions/", views.session_list, name="attendance_session_list"),
    path("<slug:slug>/sessions/new/", views.session_create, name="attendance_session_create"),
    path(
        
        "<slug:slug>/sessions/<int:session_id>/mark/",
        views.session_mark,
        name="attendance_session_mark",
    ),
    path("my/", views.my_attendance, name="my_attendance"),
    path("lecturer/", views.lecturer_home, name="lecturer_home"),
]
