from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone


LANGUAGE_CHOICES = [
    ("en", "English"),
    ("lg", "Luganda"),
    ("xog", "Lusoga"),
    ("nyn", "Runyankole"),
    ("sw", "Swahili"),
]


class SchoolConnectUser(models.Model):
    """A verified phone or student PRN identity linked to an account."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="school_connect_identities",
    )
    phone_number = models.CharField(max_length=32, blank=True, db_index=True)
    student = models.ForeignKey(
        "api.Student",
        on_delete=models.CASCADE,
        related_name="school_connect_identities",
        null=True,
        blank=True,
    )
    student_prn = models.CharField(max_length=100, blank=True, db_index=True)
    is_phone_verified = models.BooleanField(default=False)
    is_prn_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "student_prn"],
                condition=~Q(student_prn=""),
                name="chat_unique_user_student_prn",
            ),
        ]

    def clean(self):
        self.phone_number = self.phone_number.strip()
        self.student_prn = self.student_prn.strip().upper()
        if not self.phone_number and not self.student and not self.student_prn:
            raise ValidationError("Add a phone number or student PRN identity.")
        if self.student and self.student_prn and self.student.payment_code:
            if self.student_prn != self.student.payment_code.strip().upper():
                raise ValidationError("The PRN must match the linked student's SchoolPay PRN.")

    def save(self, *args, **kwargs):
        self.phone_number = self.phone_number.strip()
        self.student_prn = self.student_prn.strip().upper()
        super().save(*args, **kwargs)

    def __str__(self):
        identity = self.student_prn or self.phone_number or str(self.user)
        return f"{self.user}: {identity}"


class Conversation(models.Model):
    class Kind(models.TextChoices):
        DIRECT = "DIRECT", "One-to-one chat"
        GROUP = "GROUP", "Group chat"
        BROADCAST = "BROADCAST", "Broadcast"
        AI = "AI", "AI assistant"

    kind = models.CharField(max_length=12, choices=Kind.choices, default=Kind.DIRECT)
    title = models.CharField(max_length=160, blank=True)
    school = models.ForeignKey(
        "api.School",
        on_delete=models.CASCADE,
        related_name="school_connect_conversations",
        null=True,
        blank=True,
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="school_connect_conversations",
        blank=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="school_connect_created_conversations",
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-updated_at", "-id"]

    def __str__(self):
        return self.title or f"{self.get_kind_display()} #{self.pk or 'new'}"


class ConnectionRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACCEPTED = "ACCEPTED", "Accepted"
        REJECTED = "REJECTED", "Rejected"

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_school_connect_requests",
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_school_connect_requests",
    )
    student = models.ForeignKey(
        "api.Student",
        on_delete=models.SET_NULL,
        related_name="school_connect_requests",
        null=True,
        blank=True,
    )
    student_prn = models.CharField(max_length=100, blank=True, db_index=True)
    phone_number = models.CharField(max_length=32, blank=True, db_index=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["sender", "recipient"],
                name="chat_unique_connection_request_pair",
            )
        ]

    def clean(self):
        if self.sender_id == self.recipient_id:
            raise ValidationError("A user cannot send a connection request to themselves.")
        self.student_prn = (self.student_prn or "").strip().upper()
        self.phone_number = (self.phone_number or "").strip()

    def accept(self):
        self.status = self.Status.ACCEPTED
        self.responded_at = timezone.now()
        self.save(update_fields=["status", "responded_at"])

        conversation = (
            Conversation.objects.filter(kind=Conversation.Kind.DIRECT, is_active=True)
            .filter(participants=self.sender)
            .filter(participants=self.recipient)
            .distinct()
            .order_by("-updated_at")
            .first()
        )
        if not conversation:
            conversation = Conversation.objects.create(
                kind=Conversation.Kind.DIRECT,
                title=f"{self.sender} <> {self.recipient}",
                created_by=self.sender,
            )
        conversation.participants.add(self.sender, self.recipient)
        conversation.updated_at = timezone.now()
        conversation.save(update_fields=["updated_at"])
        return conversation

    def __str__(self):
        return f"{self.sender} -> {self.recipient} ({self.status})"


class Message(models.Model):
    class MediaStatus(models.TextChoices):
        NONE = "NONE", "No media"
        PENDING = "PENDING", "Pending"
        READY = "READY", "Ready"
        FAILED = "FAILED", "Failed"

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="school_connect_messages",
        null=True,
        blank=True,
    )
    text = models.TextField(blank=True)
    voice_note = models.FileField(upload_to="school_connect/voice_notes/%Y/%m/", blank=True)
    video = models.FileField(upload_to="school_connect/videos/%Y/%m/", blank=True)
    media_status = models.CharField(
        max_length=12,
        choices=MediaStatus.choices,
        default=MediaStatus.NONE,
    )
    language_code = models.CharField(max_length=8, choices=LANGUAGE_CHOICES, default="en")
    timestamp = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)
    dispatch_summary = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["timestamp", "id"]

    def clean(self):
        if not self.text.strip() and not self.voice_note and not self.video:
            raise ValidationError("A message must contain text, a voice note, or a video.")

    def __str__(self):
        return f"Message #{self.pk or 'new'} in conversation {self.conversation_id}"


class StudentFeeQueryLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="school_connect_fee_queries",
        null=True,
        blank=True,
    )
    student = models.ForeignKey(
        "api.Student",
        on_delete=models.SET_NULL,
        related_name="school_connect_fee_queries",
        null=True,
        blank=True,
    )
    requested_identifier = models.CharField(max_length=120)
    verified = models.BooleanField(default=False)
    decision = models.CharField(max_length=32)
    request_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "created_at"])]

    def __str__(self):
        return f"Fee query {self.decision} by {self.user_id or 'anonymous'} at {self.created_at}"


class DeviceToken(models.Model):
    class Platform(models.TextChoices):
        ANDROID = "ANDROID", "Android"
        IOS = "IOS", "iOS"
        WEB = "WEB", "Web"
        OTHER = "OTHER", "Other"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="school_connect_devices",
    )
    token = models.CharField(max_length=4096, unique=True)
    platform = models.CharField(max_length=10, choices=Platform.choices, default=Platform.OTHER)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.user} ({self.platform})"
