from django.urls import path

from . import views


app_name = "school_connect"

urlpatterns = [
    path("lookup/", views.lookup_contact, name="lookup"),
    path("connections/request/", views.request_connection, name="request-connection"),
    path("connections/respond/", views.respond_connection, name="respond-connection"),
    path("fee-inquiry/", views.fee_inquiry, name="fee-inquiry"),
    path("devices/register/", views.register_device_token, name="register-device-token"),
    path("broadcast/", views.create_broadcast, name="broadcast"),
]
