
from django.urls import path

from .learning_views import (
    learning_assignment_submit,
    learning_lesson,
    learning_overview,
    learning_progress,
    learning_quiz,
    learning_quiz_submit,
    learning_subject,
)

urlpatterns = [
    path("overview/", learning_overview, name="learning_overview"),
    path("subject/", learning_subject, name="learning_subject"),
    path("lesson/", learning_lesson, name="learning_lesson"),
    path("progress/", learning_progress, name="learning_progress"),
    path("assignment/submit/", learning_assignment_submit, name="learning_assignment_submit"),
    path("quiz/", learning_quiz, name="learning_quiz"),
    path("quiz/submit/", learning_quiz_submit, name="learning_quiz_submit"),
]
