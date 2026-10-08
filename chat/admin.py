from django.contrib import admin, messages

from api.models import Staff
from .broadcast import publish_broadcast
from .models import ConnectionRequest, Conversation, DeviceToken, Message, SchoolConnectUser, StudentFeeQueryLog


def _can_publish(user):
    return user.is_superuser or Staff.objects.filter(user=user, role="DIRECTOR").exists()


@admin.register(SchoolConnectUser)
class SchoolConnectUserAdmin(admin.ModelAdmin):
    list_display = ("user", "phone_number", "student_prn", "student", "is_phone_verified", "is_prn_verified", "is_active")
    list_filter = ("is_phone_verified", "is_prn_verified", "is_active")
    search_fields = ("user__username", "user__email", "phone_number", "student_prn", "student__full_name")


@admin.register(ConnectionRequest)
class ConnectionRequestAdmin(admin.ModelAdmin):
    list_display = ("sender", "recipient", "student", "status", "created_at", "responded_at")
    list_filter = ("status", "created_at")
    search_fields = ("sender__username", "recipient__username", "student__full_name", "student_prn", "phone_number")


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("title", "kind", "school", "created_by", "is_active", "created_at", "updated_at")
    list_filter = ("kind", "school", "is_active")
    search_fields = ("title", "school__name", "created_by__username")
    filter_horizontal = ("participants",)


@admin.action(description="Publish selected School Connect broadcasts")
def publish_selected_broadcasts(modeladmin, request, queryset):
    if not _can_publish(request.user):
        modeladmin.message_user(request, "Director access required.", level=messages.ERROR)
        return

    staff_school_id = None
    if not request.user.is_superuser:
        staff_school_id = Staff.objects.filter(
            user=request.user,
            role="DIRECTOR",
        ).values_list("school_id", flat=True).first()

    published = 0
    skipped = 0
    for message in queryset.select_related("conversation"):
        if message.conversation.kind != Conversation.Kind.BROADCAST:
            skipped += 1
            continue
        if staff_school_id and message.conversation.school_id != staff_school_id:
            skipped += 1
            continue
        try:
            publish_broadcast(message)
            published += 1
        except ValueError:
            skipped += 1

    modeladmin.message_user(
        request,
        f"Published {published} broadcast(s); skipped {skipped}.",
        level=messages.SUCCESS if published else messages.WARNING,
    )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "sender", "language_code", "timestamp", "published_at")
    list_filter = ("conversation__kind", "language_code", "media_status", "published_at")
    search_fields = ("text", "conversation__title", "sender__username")
    readonly_fields = ("timestamp", "published_at", "dispatch_summary")
    actions = (publish_selected_broadcasts,)


@admin.register(DeviceToken)
class DeviceTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "token_preview", "platform", "is_active", "updated_at")
    list_filter = ("platform", "is_active")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("created_at", "updated_at")

    @admin.display(description="Token")
    def token_preview(self, obj):
        return f"{obj.token[:12]}..." if obj.token else ""


@admin.register(StudentFeeQueryLog)
class StudentFeeQueryLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "student", "requested_identifier", "verified", "decision", "request_ip")
    list_filter = ("verified", "decision", "created_at")
    search_fields = ("user__username", "requested_identifier", "student__full_name")
    readonly_fields = tuple(field.name for field in StudentFeeQueryLog._meta.fields)
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
