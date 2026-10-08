import json
import logging

from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Conversation, DeviceToken, Message


logger = logging.getLogger(__name__)


def _recipients(conversation):
    devices = DeviceToken.objects.filter(is_active=True).select_related("user")
    if conversation.school_id:
        devices = devices.filter(
            Q(user__school_id=conversation.school_id)
            | Q(user__parent_profile__students__school_id=conversation.school_id)
            | Q(user__school_connect_identities__student__school_id=conversation.school_id)
        ).distinct()
    return devices


def _message_payload(message):
    return {
        "id": message.pk,
        "conversation_id": message.conversation_id,
        "sender_id": message.sender_id,
        "text": message.text,
        "language_code": message.language_code,
        "timestamp": (message.timestamp or timezone.now()).isoformat(),
    }


def _firebase_app():
    service_account_json = getattr(settings, "FIREBASE_SERVICE_ACCOUNT_JSON", "")
    if not service_account_json:
        return None

    import firebase_admin
    from firebase_admin import credentials

    try:
        return firebase_admin.get_app("school-connect")
    except ValueError:
        return firebase_admin.initialize_app(
            credentials.Certificate(json.loads(service_account_json)),
            name="school-connect",
        )


def _send_push(devices, message):
    try:
        app = _firebase_app()
    except Exception:
        logger.exception("School Connect Firebase initialization failed")
        return {"sent": 0, "failed": len(devices), "configured": False}

    if app is None:
        return {"sent": 0, "failed": 0, "configured": False}

    from firebase_admin import messaging

    sent = 0
    failed = 0
    tokens = [device.token for device in devices]
    for start in range(0, len(tokens), 500):
        batch = tokens[start : start + 500]
        try:
            result = messaging.send_each_for_multicast(
                messaging.MulticastMessage(
                    notification=messaging.Notification(
                        title=message.conversation.title or "School Connect",
                        body=message.text[:500] or "You have a new School Connect message.",
                    ),
                    data={
                        "conversation_id": str(message.conversation_id),
                        "message_id": str(message.pk),
                    },
                    tokens=batch,
                ),
                app=app,
            )
            sent += result.success_count
            failed += result.failure_count
        except Exception:
            logger.exception("School Connect push batch failed")
            failed += len(batch)
    return {"sent": sent, "failed": failed, "configured": True}


def publish_broadcast(message_or_id):
    """Dispatch a persisted broadcast over Channels and configured Firebase."""
    message_id = getattr(message_or_id, "pk", message_or_id)
    message = Message.objects.select_related("conversation", "sender").get(pk=message_id)
    if message.conversation.kind != Conversation.Kind.BROADCAST:
        raise ValueError("Only broadcast-conversation messages can be published.")
    if message.published_at:
        raise ValueError("This broadcast message has already been published.")

    devices = list(_recipients(message.conversation))
    payload = _message_payload(message)
    channel_layer = get_channel_layer()
    socket_users = 0
    if channel_layer:
        for user_id in {device.user_id for device in devices}:
            try:
                async_to_sync(channel_layer.group_send)(
                    f"school_connect_user_{user_id}",
                    {"type": "school_connect.message", "message": payload},
                )
                socket_users += 1
            except Exception:
                logger.exception("School Connect WebSocket dispatch failed for user %s", user_id)

    push_result = _send_push(devices, message)
    summary = {
        "active_devices": len(devices),
        "websocket_users": socket_users,
        "push_sent": push_result["sent"],
        "push_failed": push_result["failed"],
        "push_configured": push_result["configured"],
    }
    message.published_at = timezone.now()
    message.dispatch_summary = summary
    message.save(update_fields=["published_at", "dispatch_summary"])
    return summary
