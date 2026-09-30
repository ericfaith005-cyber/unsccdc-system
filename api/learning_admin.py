
from django.contrib import admin

from .learning_models import (
    LearningAssignment,
    LearningAssignmentSubmission,
    LearningLesson,
    LearningProgress,
    LearningQuiz,
    LearningQuizAttempt,
    LearningQuizQuestion,
    LearningTopic,
)


@admin.register(LearningTopic)
class LearningTopicAdmin(admin.ModelAdmin):
    list_display = ("title", "school", "subject", "class_name", "order", "is_published")
    list_filter = ("school", "subject", "class_name", "is_published")
    search_fields = ("title", "description", "class_name")


@admin.register(LearningLesson)
class LearningLessonAdmin(admin.ModelAdmin):
    list_display = ("title", "topic", "duration_minutes", "order", "is_published", "updated_at")
    list_filter = ("is_published", "topic__school", "topic__subject")
    search_fields = ("title", "summary", "content")
    ordering = ("topic__subject__name", "topic__order", "order")


@admin.register(LearningAssignment)
class LearningAssignmentAdmin(admin.ModelAdmin):
    list_display = ("title", "school", "subject", "class_name", "due_at", "is_published")
    list_filter = ("school", "subject", "class_name", "is_published")
    search_fields = ("title", "instructions")


@admin.register(LearningQuiz)
class LearningQuizAdmin(admin.ModelAdmin):
    list_display = ("title", "school", "subject", "class_name", "pass_mark", "is_published")
    list_filter = ("school", "subject", "class_name", "is_published")
    search_fields = ("title", "instructions")


@admin.register(LearningQuizQuestion)
class LearningQuizQuestionAdmin(admin.ModelAdmin):
    list_display = ("quiz", "order", "points", "correct_option")
    list_filter = ("quiz", "correct_option")
    search_fields = ("question",)


@admin.register(LearningProgress)
class LearningProgressAdmin(admin.ModelAdmin):
    list_display = ("student", "lesson", "progress_percent", "completed", "updated_at")
    list_filter = ("completed", "lesson__topic__subject")
    search_fields = ("student__full_name", "lesson__title")
    readonly_fields = (
        "student",
        "lesson",
        "progress_percent",
        "last_position_seconds",
        "completed",
        "started_at",
        "completed_at",
        "updated_at",
    )


@admin.register(LearningQuizAttempt)
class LearningQuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("student", "quiz", "score", "total_points", "passed", "submitted_at")
    list_filter = ("passed", "quiz__subject")
    search_fields = ("student__full_name", "quiz__title")
    readonly_fields = (
        "student",
        "quiz",
        "score",
        "total_points",
        "passed",
        "answers_json",
        "submitted_at",
    )


@admin.register(LearningAssignmentSubmission)
class LearningAssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ("student", "assignment", "submitted_at", "updated_at")
    list_filter = ("assignment__subject",)
    search_fields = ("student__full_name", "assignment__title", "response_text")
    readonly_fields = (
        "student",
        "assignment",
        "response_text",
        "submitted_at",
        "updated_at",
    )
