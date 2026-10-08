from django.urls import path

from .consumers import SchoolConnectConsumer


websocket_urlpatterns = [
    path("ws/school-connect/", SchoolConnectConsumer.as_asgi(), name="school-connect-user-ws"),
    path(
        "ws/school-connect/<int:conversation_id>/",
        SchoolConnectConsumer.as_asgi(),
        name="school-connect-conversation-ws",
    ),
]
