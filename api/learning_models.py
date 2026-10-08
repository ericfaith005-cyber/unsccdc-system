
from django.db import models


class LearningTopic(models.Model):
    school = models.ForeignKey(
        "School",
        on_delete=models.CASCADE,
        related_name="learning_topics",
    )
    subject = models.ForeignKey(
        "Subject",
        on_delete=models.CASCADE,
        related_name="learning_topics",
    )
    class_name = models.CharField(max_length=100, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["subject__name", "order", "title"]
        indexes = [
            models.Index(fields=["school", "class_name", "is_published"]),
        ]

    def __str__(self):
        return f"{self.subject.name} - {self.class_name} - {self.title}"


class LearningLesson(models.Model):
    topic = models.ForeignKey(
        LearningTopic,
        on_delete=models.CASCADE,
        related_name="lessons",
    )
    title = models.CharField(max_length=255)
    summary = models.TextField(blank=True)
    content = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    document_url = models.URLField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=30)
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["topic__order", "order", "title"]
        indexes = [
            models.Index(fields=["topic", "is_published"]),
        ]

    def __str__(self):
        return self.title


class LearningAssignment(models.Model):
    school = models.ForeignKey(
        "School",
        on_delete=models.CASCADE,
        related_name="learning_assignments",
    )
    subject = models.ForeignKey(
        "Subject",
        on_delete=models.CASCADE,
        related_name="learning_assignments",
    )
    class_name = models.CharField(max_length=100, db_index=True)
    lesson = models.ForeignKey(
        LearningLesson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assignments",
    )
    title = models.CharField(max_length=255)
    instructions = models.TextField(blank=True)
    due_at = models.DateTimeField(null=True, blank=True)
    total_points = models.PositiveIntegerField(default=100)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["due_at", "-created_at"]

    def __str__(self):
        return self.title

class LearningQuiz(models.Model):
    school = models.ForeignKey(
        "School",
        on_delete=models.CASCADE,
        related_name="learning_quizzes",
    )
    subject = models.ForeignKey(
        "Subject",
        on_delete=models.CASCADE,
        related_name="learning_quizzes",
    )
    class_name = models.CharField(max_length=100, db_index=True)
    lesson = models.ForeignKey(
        LearningLesson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quizzes",
    )
    title = models.CharField(max_length=255)
    instructions = models.TextField(blank=True)
    pass_mark = models.PositiveIntegerField(default=50)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class LearningQuizQuestion(models.Model):
    quiz = models.ForeignKey(
        LearningQuiz,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    question = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500, blank=True)
    option_d = models.CharField(max_length=500, blank=True)
    correct_option = models.CharField(
        max_length=1,
        choices=[
            ("A", "A"),
            ("B", "B"),
            ("C", "C"),
            ("D", "D"),
        ],
    )
    explanation = models.TextField(blank=True)
    points = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.quiz.title} - Q{self.order + 1}"


class LearningProgress(models.Model):
    student = models.ForeignKey(
        "Student",
        on_delete=models.CASCADE,
        related_name="learning_progress",
    )
    lesson = models.ForeignKey(
        LearningLesson,
        on_delete=models.CASCADE,
        related_name="progress_records",
    )
    progress_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )
    last_position_seconds = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "lesson"],
                name="unique_learning_progress_student_lesson",
            ),
        ]

    def __str__(self):
        return f"{self.student.full_name} - {self.lesson.title}"


class LearningQuizAttempt(models.Model):
    student = models.ForeignKey(
        "Student",
        on_delete=models.CASCADE,
        related_name="learning_quiz_attempts",
    )
    quiz = models.ForeignKey(
        LearningQuiz,
        on_delete=models.CASCADE,
        related_name="attempts",
    )
    score = models.PositiveIntegerField(default=0)
    total_points = models.PositiveIntegerField(default=0)
    passed = models.BooleanField(default=False)
    answers_json = models.JSONField(default=dict)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.student.full_name} - {self.quiz.title} - {self.score}/{self.total_points}"


class LearningAssignmentSubmission(models.Model):
    student = models.ForeignKey(
        "Student",
        on_delete=models.CASCADE,
        related_name="learning_assignment_submissions",
    )
    assignment = models.ForeignKey(
        LearningAssignment,
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    response_text = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "assignment"],
                name="unique_learning_assignment_submission",
            ),
        ]

    def __str__(self):
        return f"{self.student.full_name} - {self.assignment.title}"
