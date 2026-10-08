import json
import logging

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from api.models import Parent, Staff, Student
from .ai_assistant import process_fee_inquiry
from .broadcast import publish_broadcast
from .models import ConnectionRequest, Conversation, DeviceToken, Message, SchoolConnectUser

User = get_user_model()


logger = logging.getLogger(__name__)


def _json_body(request):
    try:
        data = json.loads(request.body or b"{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _is_director(user):
    if user.is_superuser:
        return True
    return Staff.objects.filter(user=user, role="DIRECTOR").exists()


def _director_school(user):
    if user.is_superuser:
        return None
    return Staff.objects.filter(user=user, role="DIRECTOR").values_list("school_id", flat=True).first()


def _resolve_contact(identifier):
    normalized = str(identifier or "").strip()
    if not normalized:
        return None

    student = (
        Student.objects.filter(
            Q(payment_code__iexact=normalized)
            | Q(account_number__iexact=normalized)
            | Q(parent_link__phone_number__iexact=normalized)
        )
        .select_related("school", "parent_link")
        .first()
    )
    if student:
        parent = student.parent_link
        user = parent.user if parent and parent.user_id else None
        identity = SchoolConnectUser.objects.filter(student=student, is_active=True).order_by("-is_prn_verified", "-created_at").first()
        return {
            "user_id": user.pk if user else None,
            "contact_name": getattr(user, "get_full_name", lambda: None)() or (parent.full_name if parent else student.full_name),
            "phone_number": (parent.phone_number if parent else "") or (identity.phone_number if identity else ""),
            "student_id": student.pk,
            "student": {
                "id": student.pk,
                "full_name": student.full_name,
                "payment_code": student.payment_code,
                "school": student.school.name if student.school_id else None,
            },
            "verified": bool(identity and identity.is_prn_verified),
            "student_prn": student.payment_code or "",
        }

    identity = (
        SchoolConnectUser.objects.filter(
            Q(phone_number__iexact=normalized)
            | Q(student_prn__iexact=normalized)
        )
        .select_related("user", "student")
        .order_by("-is_phone_verified", "-is_prn_verified", "-created_at")
        .first()
    )
    if identity:
        user = identity.user
        student = identity.student
        return {
            "user_id": user.pk,
            "contact_name": user.get_full_name() or getattr(student, "full_name", "") or user.username,
            "phone_number": identity.phone_number,
            "student_id": student.pk if student else None,
            "student": {
                "id": student.pk if student else None,
                "full_name": student.full_name if student else "",
                "payment_code": getattr(student, "payment_code", "") if student else "",
                "school": student.school.name if student and student.school_id else None,
            },
            "verified": bool(identity.is_phone_verified or identity.is_prn_verified),
            "student_prn": identity.student_prn,
        }

    parent = Parent.objects.filter(phone_number__iexact=normalized).select_related("user").first()
    if parent and parent.user_id:
        student = Student.objects.filter(parent_link=parent).order_by("-id").first()
        return {
            "user_id": parent.user_id,
            "contact_name": parent.full_name or parent.user.get_full_name() or parent.user.username,
            "phone_number": parent.phone_number,
            "student_id": student.pk if student else None,
            "student": {
                "id": student.pk if student else None,
                "full_name": student.full_name if student else "",
                "payment_code": student.payment_code if student else "",
                "school": student.school.name if student and student.school_id else None,
            },
            "verified": bool(student and student.payment_code),
            "student_prn": student.payment_code if student else "",
        }

    return None


@require_POST
def lookup_contact(request):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required."}, status=401)

    data = _json_body(request)
    if data is None:
        return JsonResponse({"detail": "Request body must be a JSON object."}, status=400)

    identifier = str(data.get("identifier") or data.get("student_prn") or data.get("phone_number") or "").strip()
    if not identifier:
        return JsonResponse({"detail": "A PRN or phone number is required."}, status=400)

    contact = _resolve_contact(identifier)
    if not contact:
        return JsonResponse({"found": False, "detail": "No matching student or parent was found."}, status=404)

    return JsonResponse({"found": True, "contact": contact, "student": contact.get("student"), "user_id": contact.get("user_id")})


@require_POST
def request_connection(request):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required."}, status=401)

    data = _json_body(request)
    if data is None:
        return JsonResponse({"detail": "Request body must be a JSON object."}, status=400)

    identifier = str(data.get("identifier") or data.get("student_prn") or data.get("phone_number") or "").strip()
    if not identifier:
        return JsonResponse({"detail": "A PRN or phone number is required."}, status=400)

    target = _resolve_contact(identifier)
    if not target or not target.get("user_id"):
        return JsonResponse({"detail": "No matching user could be reached."}, status=404)
    if int(target["user_id"]) == request.user.pk:
        return JsonResponse({"detail": "You cannot send a connection request to yourself."}, status=400)

    created_at = timezone.now()
    request_obj, created = ConnectionRequest.objects.get_or_create(
        sender=request.user,
        recipient_id=target["user_id"],
        defaults={
            "student_id": target.get("student_id"),
            "student_prn": target.get("student_prn") or "",
            "phone_number": target.get("phone_number") or "",
            "message": str(data.get("message", "")).strip(),
            "status": ConnectionRequest.Status.PENDING,
        },
    )
    if not created:
        request_obj.status = ConnectionRequest.Status.PENDING
        request_obj.student_id = target.get("student_id")
        request_obj.student_prn = target.get("student_prn") or ""
        request_obj.phone_number = target.get("phone_number") or ""
        request_obj.message = str(data.get("message", "")).strip()
        request_obj.responded_at = None
        request_obj.save(update_fields=["status", "student_id", "student_prn", "phone_number", "message", "responded_at"])

    return JsonResponse({
        "ok": True,
        "request_id": request_obj.pk,
        "status": request_obj.status,
        "requested_user_id": target["user_id"],
        "created": created,
    }, status=201 if created else 200)


@require_POST
def respond_connection(request):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required."}, status=401)

    data = _json_body(request)
    if data is None:
        return JsonResponse({"detail": "Request body must be a JSON object."}, status=400)

    request_id = data.get("request_id")
    action = str(data.get("action", "")).strip().lower()
    if not request_id:
        return JsonResponse({"detail": "request_id is required."}, status=400)
    if action not in {"accept", "reject"}:
        return JsonResponse({"detail": "action must be 'accept' or 'reject'."}, status=400)

    connection = ConnectionRequest.objects.filter(pk=request_id, recipient=request.user).select_related("sender", "recipient").first()
    if not connection:
        return JsonResponse({"detail": "Connection request not found for this user."}, status=404)

    if action == "accept":
        conversation = connection.accept()
        status = connection.status
        return JsonResponse({"ok": True, "status": status, "request_id": connection.pk, "conversation_id": conversation.pk}, status=200)

    connection.status = ConnectionRequest.Status.REJECTED
    connection.responded_at = timezone.now()
    connection.save(update_fields=["status", "responded_at"])
    return JsonResponse({"ok": True, "status": connection.status, "request_id": connection.pk})


@require_POST
def fee_inquiry(request):
    data = _json_body(request)
    if data is None:
        return JsonResponse({"detail": "Request body must be a JSON object."}, status=400)
    identifier = data.get("student_prn_or_id", "")
    response_text = process_fee_inquiry(
        request.user,
        identifier,
        request_ip=request.META.get("REMOTE_ADDR"),
    )
    if response_text.startswith("Permission denied:"):
        status = 401 if not request.user.is_authenticated else 403
        return JsonResponse({"detail": response_text}, status=status)
    return JsonResponse({"text": response_text})


@require_POST
def register_device_token(request):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required."}, status=401)
    data = _json_body(request)
    if data is None:
        return JsonResponse({"detail": "Request body must be a JSON object."}, status=400)

    token = str(data.get("token", "")).strip()
    platform = str(data.get("platform", DeviceToken.Platform.OTHER)).strip().upper()
    valid_platforms = {choice for choice, _label in DeviceToken.Platform.choices}
    if not token or len(token) > 4096 or platform not in valid_platforms:
        return JsonResponse({"detail": "A valid token and platform are required."}, status=400)

    device, _created = DeviceToken.objects.update_or_create(
        token=token,
        defaults={"user": request.user, "platform": platform, "is_active": True},
    )
    return JsonResponse({"ok": True, "device_id": device.pk})


@require_POST
def create_broadcast(request):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required."}, status=401)
    if not _is_director(request.user):
        return JsonResponse({"detail": "Director access required."}, status=403)

    data = _json_body(request)
    if data is None:
        return JsonResponse({"detail": "Request body must be a JSON object."}, status=400)

    text = str(data.get("text", "")).strip()
    title = str(data.get("title", "")).strip()[:160]
    if not text:
        return JsonResponse({"detail": "Broadcast text is required."}, status=400)

    language_code = str(data.get("language_code", "en")).strip().lower()
    allowed_languages = {"en", "lg", "xog", "nyn", "sw"}
    if language_code not in allowed_languages:
        return JsonResponse({"detail": "Unsupported language_code."}, status=400)

    school_id = _director_school(request.user)
    if request.user.is_superuser and data.get("school_id"):
        try:
            school_id = int(data["school_id"])
        except (TypeError, ValueError):
            return JsonResponse({"detail": "school_id must be an integer."}, status=400)

    conversation = Conversation.objects.create(
        kind=Conversation.Kind.BROADCAST,
        title=title or "School Broadcast",
        school_id=school_id,
        created_by=request.user,
    )
    if not request.user.is_superuser:
        conversation.participants.add(request.user)

    translated_text = text
    if language_code != "en":
        try:
            from .utils import translate_message
            translated_text = translate_message(text, language_code)
        except Exception:
            logger.info("Broadcast translation skipped for %s because the provider is unavailable.", language_code)

    message = Message.objects.create(
        conversation=conversation,
        sender=request.user,
        text=translated_text,
        language_code=language_code,
    )
    try:
        delivery = publish_broadcast(message)
    except Exception:
        logger.exception("Broadcast %s was saved but dispatch failed", message.pk)
        return JsonResponse(
            {"ok": False, "message_id": message.pk, "detail": "Broadcast saved but dispatch failed."},
            status=503,
        )
    return JsonResponse({"ok": True, "message_id": message.pk, "delivery": delivery}, status=201)
