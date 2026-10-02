import datetime
import json
import os
import uuid

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from livekit import api

from .classroom_models import (
    ClassroomAttendance,
    ClassroomJoinRequest,
    ClassroomRecording,
    ClassroomSession,
    classroom_default_settings,
)
from .models import Staff, Student


def _classroom_response(data, status=200):
    response = JsonResponse(data, status=status)
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type, X-Sovereign-Client"
    return response


def _body(request):
    try:
        value = json.loads(request.body or "{}")
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def _clean(value):
    return str(value or "").strip()


def _staff_from_body(body):
    name = _clean(body.get("staff_name"))
    pin = _clean(body.get("pin"))
    if not name or not pin:
        return None, "Staff name and PIN are required."
    staff = Staff.objects.select_related("school").filter(full_name__iexact=name, secure_pin=pin).first()
    if not staff:
        return None, "Invalid staff classroom credentials."
    return staff, None


def _student_from_body(body):
    student_id = _clean(body.get("student_id") or body.get("account_number"))
    pin = _clean(body.get("pin"))
    if not student_id or not pin:
        return None, "Student account and PIN are required."
    student = Student.objects.select_related("school", "parent_link").filter(account_number__iexact=student_id, is_active=True).first()
    if not student:
        return None, "Student account not found."
    parent = student.parent_link
    if not parent:
        return None, "No authorized parent account is linked to this student."
    allowed = {_clean(getattr(parent, "unique_code", "")), _clean(getattr(parent, "secure_pin", ""))}
    allowed.discard("")
    if pin not in allowed:
        return None, "Invalid classroom authorization PIN."
    return student, None


def _make_session_code():
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    for _ in range(100):
        code = "".join(alphabet[uuid.uuid4().int % len(alphabet)] for _ in range(6))
        if not ClassroomSession.objects.filter(session_code=code).exists():
            return code
    raise RuntimeError("Could not generate a unique classroom code.")


def _make_room_name():
    return f"unsccdc-room-{uuid.uuid4().hex[:18]}"


def _merge_settings(current, incoming):
    settings = dict(current or classroom_default_settings())
    if isinstance(incoming, dict):
        for key, value in incoming.items():
            if key in settings:
                settings[key] = value
    return settings


def _session_payload(session):
    return {
        "id": session.id,
        "title": session.title,
        "subject_name": session.subject_name,
        "class_name": session.class_name,
        "session_code": session.session_code,
        "room_name": session.room_name,
        "status": session.status,
        "host": {"id": session.host_staff_id, "name": session.host_staff.full_name},
        "school": {"id": session.school_id, "name": session.school.name},
        "settings": session.settings or classroom_default_settings(),
        "educational_notice": session.educational_notice,
        "started_at": session.started_at.isoformat() if session.started_at else "",
        "created_at": session.created_at.isoformat(),
    }


@csrf_exempt
def classroom_create(request):
    if request.method == "OPTIONS":
        return _classroom_response({})
    if request.method != "POST":
        return _classroom_response({"message": "POST required."}, 405)
    body = _body(request)
    staff, error = _staff_from_body(body)
    if error:
        return _classroom_response({"message": error}, 401)
    title = _clean(body.get("title")) or "UNSCCDC Live Classroom"
    class_name = _clean(body.get("class_name"))
    if not class_name:
        return _classroom_response({"message": "class_name is required."}, 400)
    if ClassroomSession.objects.filter(host_staff=staff, status__in=[ClassroomSession.STATUS_WAITING, ClassroomSession.STATUS_LIVE]).exists():
        return _classroom_response({"message": "You already have an active classroom. End it before creating another."}, 409)
    session = ClassroomSession.objects.create(
        school=staff.school,
        host_staff=staff,
        title=title,
        subject_name=_clean(body.get("subject_name")),
        class_name=class_name,
        session_code=_make_session_code(),
        room_name=_make_room_name(),
        settings=_merge_settings(classroom_default_settings(), body.get("settings")),
    )
    return _classroom_response({"status": "ok", "session": _session_payload(session)})


@csrf_exempt
def classroom_info(request):
    if request.method == "OPTIONS":
        return _classroom_response({})
    if request.method != "POST":
        return _classroom_response({"message": "POST required."}, 405)
    code = _clean(_body(request).get("session_code")).upper()
    if not code:
        return _classroom_response({"message": "session_code is required."}, 400)
    session = ClassroomSession.objects.select_related("school", "host_staff").filter(session_code=code).first()
    if not session:
        return _classroom_response({"message": "Classroom code not found."}, 404)
    return _classroom_response({"status": "ok", "session": _session_payload(session)})


@csrf_exempt
def classroom_join_request(request):
    if request.method == "OPTIONS":
        return _classroom_response({})
    if request.method != "POST":
        return _classroom_response({"message": "POST required."}, 405)
    body = _body(request)
    code = _clean(body.get("session_code")).upper()
    session = ClassroomSession.objects.select_related("school", "host_staff").filter(
        session_code=code,
        status__in=[ClassroomSession.STATUS_WAITING, ClassroomSession.STATUS_LIVE],
    ).first()
    if not session:
        return _classroom_response({"message": "Active classroom not found."}, 404)
    student, error = _student_from_body(body)
    if error:
        return _classroom_response({"message": error}, 401)
    if student.school_id != session.school_id:
        return _classroom_response({"message": "This classroom belongs to another school."}, 403)
    if _clean(student.current_class) and _clean(student.current_class).lower() != session.class_name.lower():
        return _classroom_response({"message": f"This classroom is restricted to {session.class_name}."}, 403)
    existing = ClassroomJoinRequest.objects.filter(session=session, student=student).first()
    if existing:
        if existing.status == ClassroomJoinRequest.REJECTED:
            existing.status = ClassroomJoinRequest.PENDING
            existing.decided_by = None
            existing.decided_at = None
            existing.host_note = ""
            existing.requested_at = timezone.now()
            existing.save()
        return _classroom_response({"status": "ok", "request": {"id": existing.id, "state": existing.status, "name": existing.requested_by_name}, "session": {"title": session.title, "session_code": session.session_code, "status": session.status, "settings": session.settings}})
    row = ClassroomJoinRequest.objects.create(
        session=session,
        student=student,
        requested_by_name=student.full_name,
        role=ClassroomJoinRequest.ROLE_PARENT,
        status=ClassroomJoinRequest.PENDING,
    )
    return _classroom_response({"status": "ok", "request": {"id": row.id, "state": row.status, "name": row.requested_by_name}, "session": {"title": session.title, "session_code": session.session_code, "status": session.status, "settings": session.settings}, "message": "Join request submitted. Waiting for host approval."})


@csrf_exempt
def classroom_join_status(request):
    if request.method == "OPTIONS":
        return _classroom_response({})
    if request.method != "POST":
        return _classroom_response({"message": "POST required."}, 405)
    body = _body(request)
    request_id = body.get("request_id")
    if not request_id:
        return _classroom_response({"message": "request_id is required."}, 400)
    try:
        row = ClassroomJoinRequest.objects.select_related("session", "student").get(id=int(request_id))
    except (ClassroomJoinRequest.DoesNotExist, ValueError, TypeError):
        return _classroom_response({"message": "Join request not found."}, 404)
    student, error = _student_from_body(body)
    if error or not row.student_id or student.id != row.student_id:
        return _classroom_response({"message": error or "Join request identity mismatch."}, 403)
    return _classroom_response({"status": "ok", "request": {"id": row.id, "state": row.status, "host_note": row.host_note}, "session": {"status": row.session.status, "title": row.session.title, "session_code": row.session.session_code, "settings": row.session.settings, "educational_notice": row.session.educational_notice}})


@csrf_exempt
def classroom_requests(request):
    if request.method == "OPTIONS":
        return _classroom_response({})
    if request.method != "POST":
        return _classroom_response({"message": "POST required."}, 405)
    body = _body(request)
    staff, error = _staff_from_body(body)
    if error:
        return _classroom_response({"message": error}, 401)
    session = ClassroomSession.objects.filter(id=body.get("session_id"), host_staff=staff, status__in=[ClassroomSession.STATUS_WAITING, ClassroomSession.STATUS_LIVE]).first()
    if not session:
        return _classroom_response({"message": "Classroom session not found."}, 404)
    queryset = session.join_requests.select_related("student", "staff", "decided_by")
    if bool(body.get("pending_only", True)):
        queryset = queryset.filter(status=ClassroomJoinRequest.PENDING)
    requests = []
    for row in queryset.order_by("status", "-requested_at"):
        requests.append({"id": row.id, "name": row.requested_by_name, "role": row.role, "status": row.status, "student_id": row.student.account_number if row.student_id else "", "requested_at": row.requested_at.isoformat(), "host_note": row.host_note})
    return _classroom_response({"status": "ok", "session": {"id": session.id, "title": session.title, "session_code": session.session_code}, "requests": requests})


@csrf_exempt
def classroom_decision(request):
    if request.method == "OPTIONS":
        return _classroom_response({})
    if request.method != "POST":
        return _classroom_response({"message": "POST required."}, 405)
    body = _body(request)
    staff, error = _staff_from_body(body)
    if error:
        return _classroom_response({"message": error}, 401)
    try:
        row = ClassroomJoinRequest.objects.select_related("session").get(id=int(body.get("request_id")))
    except (ClassroomJoinRequest.DoesNotExist, ValueError, TypeError):
        return _classroom_response({"message": "Join request not found."}, 404)
    if row.session.host_staff_id != staff.id:
        return _classroom_response({"message": "You are not the host of this classroom."}, 403)
    if row.session.status == ClassroomSession.STATUS_ENDED:
        return _classroom_response({"message": "This classroom has ended."}, 409)
    approved = bool(body.get("approved", False))
    row.status = ClassroomJoinRequest.APPROVED if approved else ClassroomJoinRequest.REJECTED
    row.host_note = _clean(body.get("host_note"))
    row.decided_by = staff
    row.decided_at = timezone.now()
    row.save(update_fields=["status", "host_note", "decided_by", "decided_at"])
    return _classroom_response({"status": "ok", "request": {"id": row.id, "state": row.status, "name": row.requested_by_name}})


@csrf_exempt
def classroom_settings(request):
    if request.method == "OPTIONS":
        return _classroom_response({})
    if request.method != "POST":
        return _classroom_response({"message": "POST required."}, 405)
    body = _body(request)
    staff, error = _staff_from_body(body)
    if error:
        return _classroom_response({"message": error}, 401)
    session = ClassroomSession.objects.filter(id=body.get("session_id"), host_staff=staff, status__in=[ClassroomSession.STATUS_WAITING, ClassroomSession.STATUS_LIVE]).first()
    if not session:
        return _classroom_response({"message": "Classroom session not found."}, 404)
    session.settings = _merge_settings(session.settings, body.get("settings"))
    session.save(update_fields=["settings"])
    return _classroom_response({"status": "ok", "settings": session.settings})


@csrf_exempt
def classroom_end(request):
    if request.method == "OPTIONS":
        return _classroom_response({})
    if request.method != "POST":
        return _classroom_response({"message": "POST required."}, 405)
    body = _body(request)
    staff, error = _staff_from_body(body)
    if error:
        return _classroom_response({"message": error}, 401)
    session = ClassroomSession.objects.filter(id=body.get("session_id"), host_staff=staff, status__in=[ClassroomSession.STATUS_WAITING, ClassroomSession.STATUS_LIVE]).first()
    if not session:
        return _classroom_response({"message": "Classroom session not found."}, 404)
    session.status = ClassroomSession.STATUS_ENDED
    session.ended_at = timezone.now()
    session.save(update_fields=["status", "ended_at"])
    return _classroom_response({"status": "ok", "message": "Classroom ended.", "session_id": session.id})


def _legacy_token_fallback(request):
    from . import views as legacy_views
    return legacy_views.classroom_token(request)


@csrf_exempt
def classroom_token(request):
    if request.method == "OPTIONS":
        return _classroom_response({})
    if request.method != "POST":
        return _classroom_response({"msg": "POST method required."}, 405)
    body = _body(request)
    if not _clean(body.get("session_code")):
        return _legacy_token_fallback(request)

    session_code = _clean(body.get("session_code")).upper()
    mode = _clean(body.get("mode") or "parent").lower()
    session = ClassroomSession.objects.select_related("school", "host_staff").filter(session_code=session_code, status__in=[ClassroomSession.STATUS_WAITING, ClassroomSession.STATUS_LIVE]).first()
    if not session:
        return _classroom_response({"msg": "Active classroom not found."}, 404)

    participant = None
    host_staff = None

    if mode == "staff":
        host_staff, error = _staff_from_body(body)
        if error:
            return _classroom_response({"msg": error}, 401)
        if host_staff.id != session.host_staff_id:
            return _classroom_response({"msg": "Only the classroom host can open the host session."}, 403)
        participant_role = "host"
        display_name = host_staff.full_name
        if session.status == ClassroomSession.STATUS_WAITING:
            session.status = ClassroomSession.STATUS_LIVE
            session.started_at = timezone.now()
            session.save(update_fields=["status", "started_at"])
    else:
        participant, error = _student_from_body(body)
        if error:
            return _classroom_response({"msg": error}, 401)
        if participant.school_id != session.school_id:
            return _classroom_response({"msg": "This classroom belongs to another school."}, 403)
        request_id = body.get("join_request_id")
        try:
            if request_id:
                join_row = ClassroomJoinRequest.objects.select_related("student").get(id=int(request_id), session=session, student=participant)
            else:
                join_row = ClassroomJoinRequest.objects.filter(session=session, student=participant).first()
        except (ClassroomJoinRequest.DoesNotExist, ValueError, TypeError):
            join_row = None
        if not join_row:
            return _classroom_response({"msg": "You must request access to this classroom before receiving a LiveKit token."}, 403)
        if join_row.status != ClassroomJoinRequest.APPROVED:
            return _classroom_response({"msg": f"Your classroom join request is {join_row.status}.", "request_id": join_row.id, "request_status": join_row.status}, 403)
        participant_role = "participant"
        display_name = participant.full_name

    livekit_api_key = os.getenv("LIVEKIT_API_KEY")
    livekit_api_secret = os.getenv("LIVEKIT_API_SECRET")
    livekit_url = os.getenv("LIVEKIT_URL")
    if not livekit_api_key or not livekit_api_secret:
        return _classroom_response({"msg": "Live classroom service is not configured on the server."}, 503)
    if not livekit_url:
        return _classroom_response({"msg": "Live classroom server URL is not configured."}, 503)

    settings = dict(session.settings or classroom_default_settings())
    if participant_role == "participant" and settings.get("max_participants"):
        active = ClassroomAttendance.objects.filter(session=session, left_at__isnull=True).count()
        if active >= int(settings["max_participants"]):
            return _classroom_response({"msg": "This classroom is currently full."}, 409)

    identity = f"unsccdc-{uuid.uuid4().hex}"
    publish_sources = []
    if participant_role == "host":
        publish_sources = ["camera", "microphone", "screen_share", "screen_share_audio"]
    else:
        if settings.get("allow_camera", True):
            publish_sources.append("camera")
        if settings.get("allow_microphone", True):
            publish_sources.append("microphone")
        if settings.get("allow_screen_share", False):
            publish_sources.extend(["screen_share", "screen_share_audio"])

    grants = api.VideoGrants(
        room_join=True,
        room=session.room_name,
        room_admin=(participant_role == "host"),
        room_record=(participant_role == "host" and bool(settings.get("allow_recording", False))),
        can_publish=bool(publish_sources),
        can_subscribe=True,
        can_publish_data=True,
        can_publish_sources=publish_sources or None,
        can_update_own_metadata=True,
    )

    token = (
        api.AccessToken(livekit_api_key, livekit_api_secret)
        .with_identity(identity)
        .with_name(display_name)
        .with_attributes({
            "classroom_session_id": str(session.id),
            "classroom_role": participant_role,
            "school_id": str(session.school_id),
            "class_name": session.class_name,
        })
        .with_metadata(json.dumps({
            "role": participant_role,
            "session_id": session.id,
            "educational_use_only": True,
        }))
        .with_ttl(datetime.timedelta(hours=4))
        .with_grants(grants)
        .to_jwt()
    )

    if participant is not None:
        attendance, _ = ClassroomAttendance.objects.get_or_create(
            session=session,
            student=participant,
            defaults={"display_name": display_name, "role": participant_role},
        )
    else:
        attendance, _ = ClassroomAttendance.objects.get_or_create(
            session=session,
            staff=host_staff,
            defaults={"display_name": display_name, "role": participant_role},
        )
    attendance.last_seen_at = timezone.now()
    attendance.left_at = None
    attendance.save(update_fields=["last_seen_at", "left_at"])

    return _classroom_response({
        "status": "success",
        "token": token,
        "url": livekit_url,
        "room_name": session.room_name,
        "participant_identity": identity,
        "role": participant_role,
        "session_id": session.id,
        "session_code": session.session_code,
        "settings": settings,
        "educational_notice": session.educational_notice,
    })


@csrf_exempt
def classroom_recording_list(request):
    if request.method == "OPTIONS":
        return _classroom_response({})
    if request.method != "POST":
        return _classroom_response({"message": "POST required."}, 405)
    body = _body(request)
    rows = ClassroomRecording.objects.filter(session_id=body.get("session_id")).values(
        "id", "title", "notes", "topic_tags", "recording_url", "transcript_url",
        "duration_seconds", "thumbnail_url", "is_published", "published_at", "created_at",
    )
    return _classroom_response({
        "status": "ok",
        "recordings": [
            {
                **row,
                "published_at": row["published_at"].isoformat() if row["published_at"] else "",
                "created_at": row["created_at"].isoformat() if row["created_at"] else "",
            }
            for row in rows
        ],
    })
