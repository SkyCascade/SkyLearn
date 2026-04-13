from django.urls import path
from . import views

app_name = "ai_core"

urlpatterns = [
    path("lesson/generate/", views.generate_lesson, name="generate_lesson"),
    path("lesson/save-doc/", views.save_lesson_doc, name="save_lesson_doc"),
    path("lesson/<int:upload_id>/html/", views.get_lesson_html, name="get_lesson_html"),
    path("quiz/generate/", views.generate_quiz, name="generate_quiz"),
    path("chatbot/", views.chatbot_reply, name="chatbot_reply"),
]