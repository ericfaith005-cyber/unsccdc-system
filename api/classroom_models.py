from django.db import models
from django.utils import timezone


def classroom_default_settings():
    return {
        "admission_required": True,
        "allow_camera": True,
        "allow_microphone": True,
        "allow_chat": True,
        "allow_reactions": True,
        "allow_raise_hand": True,
        "allow_whiteboard": True,
        "allow_screen_share": False,
        "allow_recording": False,
        "educational_use_only": True,
        "recording_notice": (
            "This classroom may be recorded for educational use. "
            "Use of classroom content is limited to teaching, learning, "
            "revision, assessment, and academic discussion."
        ),
        "max_participants": 100,
    }


class ClassroomSession(models.Model):
    STATUS_WAITING = "waiting"
    STATUS_LIVE = "live"
    STATUS_ENDED = "ended"

    STATUS_CHOICES = [
        (STATUS_WAITING, "Waiting"),
        (STATUS_LIVE, "Live"),
        (STATUS_ENDED, "Ended"),
    ]

    school = models.ForeignKey(
        "School",
        on_delete=models.CASCADE,
        related_name="classroom_sessions",
    )
    host_staff = models.ForeignKey(
        "Staff",
        on_delete=models.PROTECT,
        related_name="hosted_classroom_sessions",
    )
    title = models.CharField(max_length=255)
    subject_name = models.CharField(max_length=150, blank=True)
    class_name = models.CharField(max_length=100, db_index=True)
    session_code = models.CharField(max_length=12, unique=True, db_index=True)
    room_name = models.CharField(max_length=120, unique=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_WAITING, db_index=True)
    settings = models.JSONField(default=classroom_default_settings)
    educational_notice = models.TextField(
        default=(
            "This classroom is for educational purposes only. "
            "Content should be used for teaching, learning, revision, "
            "assessment, and academic discussion."
        )
    )
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["school", "class_name", "status"]),
            models.Index(fields=["session_code", "status"]),
        ]

    def __str__(self):
        return f"{self.title} [{self.session_code}]"


class ClassroomJoinRequest(models.Model):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (APPROVED, "Approved"),
        (REJECTED, "Rejected"),
    ]

    ROLE_PARENT = "parent"
    ROLE_STUDENT = "student"
    ROLE_STAFF = "staff"

    ROLE_CHOICES = [
        (ROLE_PARENT, "Parent"),
        (ROLE_STUDENT, "Student"),
        (ROLE_STAFF, "Staff"),
    ]

    session = models.ForeignKey(ClassroomSession, on_delete=models.CASCADE, related_name="join_requests")
    student = models.ForeignKey(
        "Student", on_delete=models.CASCADE, null=True, blank=True, related_name="classroom_join_requests"
    )
    staff = models.ForeignKey(
        "Staff", on_delete=models.CASCADE, null=True, blank=True, related_name="classroom_join_requests"
    )
    requested_by_name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_PARENT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING, db_index=True)
    host_note = models.TextField(blank=True)
    decided_by = models.ForeignKey(
        "Staff", on_delete=models.SET_NULL, null=True, blank=True, related_name="decided_classroom_requests"
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["status", "-requested_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["session", "student"],
                condition=models.Q(student__isnull=False),
                name="unique_classroom_join_student",
            ),
        ]
        indexes = [models.Index(fields=["session", "status"])]

    def __str__(self):
        return f"{self.requested_by_name} - {self.session.title} - {self.status}"


class ClassroomAttendance(models.Model):
    session = models.ForeignKey(ClassroomSession, on_delete=models.CASCADE, related_name="attendance")
    student = models.ForeignKey(
        "Student", on_delete=models.CASCADE, null=True, blank=True, related_name="classroom_attendance"
    )
    staff = models.ForeignKey(
        "Staff", on_delete=models.CASCADE, null=True, blank=True, related_name="classroom_attendance"
    )
    display_name = models.CharField(max_length=255)
    role = models.CharField(max_length=20)
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    last_seen_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-joined_at"]
        indexes = [models.Index(fields=["session", "joined_at"])]

    def mark_seen(self):
        self.last_seen_at = timezone.now()
        self.save(update_fields=["last_seen_at"])


class ClassroomRecording(models.Model):
    session = models.ForeignKey(ClassroomSession, on_delete=models.CASCADE, related_name="recordings")
    title = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    topic_tags = models.JSONField(default=list, blank=True)
    recording_url = models.URLField(blank=True)
    transcript_url = models.URLField(blank=True)
    duration_seconds = models.PositiveIntegerField(default=0)
    thumbnail_url = models.URLField(blank=True)
    is_published = models.BooleanField(default=False, db_index=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["is_published", "created_at"])]

    def __str__(self):
        return self.title
