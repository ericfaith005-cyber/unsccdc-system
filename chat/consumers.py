from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.db.models import Q

from .models import Conversation, Message


class SchoolConnectConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4401)
            return

        self.user_group = f"school_connect_user_{self.user.pk}"
        await self.channel_layer.group_add(self.user_group, self.channel_name)

        self.conversation_id = self.scope.get("url_route", {}).get("kwargs", {}).get("conversation_id")
        self.conversation_group = None
        if self.conversation_id is not None:
            if not await self._can_access_conversation(self.conversation_id):
                await self.channel_layer.group_discard(self.user_group, self.channel_name)
                await self.close(code=4403)
                return
            self.conversation_group = f"school_connect_conversation_{self.conversation_id}"
            await self.channel_layer.group_add(self.conversation_group, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        if getattr(self, "user_group", None):
            await self.channel_layer.group_discard(self.user_group, self.channel_name)
        if getattr(self, "conversation_group", None):
            await self.channel_layer.group_discard(self.conversation_group, self.channel_name)

    async def receive_json(self, content, **kwargs):
        if not self.conversation_id or content.get("type", "message") != "message":
            await self.send_json({"error": "Connect to a conversation to send messages."})
            return

        text = str(content.get("text", "")).strip()
        language_code = str(content.get("language_code", "en")).strip().lower()
        message = await self._create_message(text, language_code)
        if message is None:
            await self.send_json({"error": "Message must contain text and a supported language."})
            return

        await self.channel_layer.group_send(
            self.conversation_group,
            {
                "type": "school_connect.message",
                "message": message,
            },
        )

    async def school_connect_message(self, event):
        await self.send_json(event["message"])

    @database_sync_to_async
    def _can_access_conversation(self, conversation_id):
        if self.user.is_superuser:
            return Conversation.objects.filter(pk=conversation_id, is_active=True).exists()
        school_id = getattr(self.user, "school_id", None)
        school_scope = Q(kind=Conversation.Kind.BROADCAST, school__isnull=True)
        if school_id:
            school_scope |= Q(kind=Conversation.Kind.BROADCAST, school_id=school_id)
        school_scope |= Q(
            kind=Conversation.Kind.BROADCAST,
            school__students_in_school__parent_link__user_id=self.user.pk,
        )
        return Conversation.objects.filter(
            Q(participants=self.user) | Q(created_by=self.user) | school_scope,
            pk=conversation_id,
            is_active=True,
        ).distinct().exists()

    @database_sync_to_async
    def _create_message(self, text, language_code):
        allowed_languages = {"en", "lg", "xog", "nyn", "sw"}
        if not text or language_code not in allowed_languages:
            return None
        conversation = Conversation.objects.filter(
            pk=self.conversation_id,
            is_active=True,
            participants=self.user,
        ).first()
        if not conversation:
            return None
        message = Message.objects.create(
            conversation=conversation,
            sender=self.user,
            text=text,
            language_code=language_code,
        )
        Conversation.objects.filter(pk=conversation.pk).update(updated_at=message.timestamp)
        return {
            "id": message.pk,
            "conversation_id": conversation.pk,
            "sender_id": self.user.pk,
            "text": message.text,
            "language_code": message.language_code,
            "timestamp": message.timestamp.isoformat(),
        }
