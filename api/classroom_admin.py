from django.contrib import admin

from .classroom_models import (
    ClassroomAttendance,
    ClassroomJoinRequest,
    ClassroomRecording,
    ClassroomSession,
)


@admin.register(ClassroomSession)
class ClassroomSessionAdmin(admin.ModelAdmin):
    list_display = ("title", "school", "class_name", "session_code", "status", "host_staff", "created_at")
    list_filter = ("status", "school")
    search_fields = ("title", "session_code", "class_name", "host_staff__full_name")
    readonly_fields = ("created_at", "started_at", "ended_at", "room_name")


@admin.register(ClassroomJoinRequest)
class ClassroomJoinRequestAdmin(admin.ModelAdmin):
    list_display = ("requested_by_name", "session", "role", "status", "requested_at", "decided_by")
    list_filter = ("status", "role")
    search_fields = ("requested_by_name", "session__title", "session__session_code", "student__account_number")


@admin.register(ClassroomAttendance)
class ClassroomAttendanceAdmin(admin.ModelAdmin):
    list_display = ("display_name", "session", "role", "joined_at", "left_at", "last_seen_at")
    list_filter = ("role", "session__school")
    search_fields = ("display_name", "session__title", "session__session_code")


@admin.register(ClassroomRecording)
class ClassroomRecordingAdmin(admin.ModelAdmin):
    list_display = ("title", "session", "is_published", "created_at", "published_at")
    list_filter = ("is_published",)
    search_fields = ("title", "notes", "session__title")
