import json
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from api.models import FeesTracker, Parent, School, Staff, Student
from .broadcast import publish_broadcast
from .models import ConnectionRequest, Conversation, DeviceToken, Message, SchoolConnectUser, StudentFeeQueryLog
from .utils import translate_message


User = get_user_model()


class FeeInquiryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="parent", password="test-password")
        self.school = School.objects.create(name="Test School")
        parent = Parent.objects.create(
            full_name="Test Parent",
            unique_code="PARENT-TEST-1",
            phone_number="+256700000001",
            user=self.user,
        )
        self.student = Student.objects.create(
            full_name="Test Student",
            current_class="P.7",
            payment_code="PRN-TEST-1",
            school=self.school,
            parent_link=parent,
        )
        FeesTracker.objects.filter(student=self.student).update(
            total_fees_due="500000",
            total_fees_paid="125000",
            due_date="2026-11-15",
        )
        self.client.force_login(self.user)

    def test_fee_details_require_verified_prn_link(self):
        response = self.client.post(
            reverse("school_connect:fee-inquiry"),
            data=json.dumps({"student_prn_or_id": "PRN-TEST-1"}),
            content_type="application/json",
            REMOTE_ADDR="203.0.113.12",
        )

        self.assertEqual(response.status_code, 403)
        self.assertNotIn("500000", response.content.decode())
        self.assertTrue(
            StudentFeeQueryLog.objects.filter(
                user=self.user,
                student=self.student,
                verified=False,
                decision="DENIED_PARENT_OR_PRN_LINK",
                request_ip="203.0.113.12",
            ).exists()
        )

    def test_verified_parent_gets_balance_and_due_date(self):
        SchoolConnectUser.objects.create(
            user=self.user,
            student=self.student,
            student_prn="PRN-TEST-1",
            is_prn_verified=True,
            is_active=True,
        )

        response = self.client.post(
            reverse("school_connect:fee-inquiry"),
            data=json.dumps({"student_prn_or_id": "PRN-TEST-1"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("UGX 375,000", response.json()["text"])
        self.assertIn("15 Nov 2026", response.json()["text"])
        self.assertTrue(StudentFeeQueryLog.objects.filter(user=self.user, verified=True).exists())


class ConnectionRequestTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(name="Connection School")
        self.sender = User.objects.create_user(username="requester", password="test-password")
        self.recipient = User.objects.create_user(username="recipient", password="test-password")
        self.recipient_parent = Parent.objects.create(
            full_name="Recipient Parent",
            unique_code="PARENT-CONNECT-2",
            phone_number="+256700000002",
            user=self.recipient,
        )
        self.student = Student.objects.create(
            full_name="Connected Student",
            current_class="S.2",
            payment_code="PRN-CONNECT-1",
            school=self.school,
            parent_link=self.recipient_parent,
        )

    def test_lookup_by_prn_returns_student_and_parent_contact(self):
        self.client.force_login(self.sender)

        response = self.client.post(
            reverse("school_connect:lookup"),
            data=json.dumps({"identifier": "PRN-CONNECT-1"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["found"])
        self.assertEqual(payload["student"]["payment_code"], "PRN-CONNECT-1")
        self.assertEqual(payload["contact"]["phone_number"], "+256700000002")

    def test_connection_request_can_be_accepted_and_creates_direct_conversation(self):
        self.client.force_login(self.sender)
        request_response = self.client.post(
            reverse("school_connect:request-connection"),
            data=json.dumps({"identifier": "PRN-CONNECT-1"}),
            content_type="application/json",
        )
        request_data = request_response.json()
        self.assertEqual(request_response.status_code, 201)
        self.assertEqual(request_data["status"], "PENDING")

        request_obj = ConnectionRequest.objects.get(pk=request_data["request_id"])
        self.client.force_login(self.recipient)
        response = self.client.post(
            reverse("school_connect:respond-connection"),
            data=json.dumps({"request_id": request_obj.pk, "action": "accept"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        request_obj.refresh_from_db()
        self.assertEqual(request_obj.status, ConnectionRequest.Status.ACCEPTED)
        conversation = Conversation.objects.filter(
            kind=Conversation.Kind.DIRECT,
            participants=self.sender,
        ).filter(participants=self.recipient).first()
        self.assertIsNotNone(conversation)


class BroadcastEndpointTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(name="Broadcast School")
        self.user = User.objects.create_user(username="director", password="test-password")
        Staff.objects.create(
            full_name="Test Director",
            user=self.user,
            school=self.school,
            phone="+256700000002",
            role="DIRECTOR",
        )
        self.client.force_login(self.user)

    def test_director_can_publish_broadcast(self):
        response = self.client.post(
            reverse("school_connect:broadcast"),
            data=json.dumps({"title": "Term update", "text": "School opens Monday."}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()["ok"])
        self.assertEqual(response.json()["delivery"]["active_devices"], 0)

    def test_non_director_cannot_broadcast(self):
        user = User.objects.create_user(username="parent-user", password="test-password")
        self.client.force_login(user)

        response = self.client.post(
            reverse("school_connect:broadcast"),
            data=json.dumps({"text": "Unauthorized broadcast"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)

    def test_published_broadcast_reaches_active_device_once(self):
        recipient = User.objects.create_user(username="broadcast-recipient", school=self.school)
        DeviceToken.objects.create(
            user=recipient,
            token="test-device-token",
            platform=DeviceToken.Platform.WEB,
            is_active=True,
        )
        conversation = Conversation.objects.create(
            kind=Conversation.Kind.BROADCAST,
            title="School notice",
            school=self.school,
            created_by=self.user,
        )
        message = Message.objects.create(
            conversation=conversation,
            sender=self.user,
            text="School opens Monday.",
        )

        result = publish_broadcast(message)

        self.assertEqual(result["active_devices"], 1)
        self.assertEqual(result["websocket_users"], 1)
        message.refresh_from_db()
        self.assertIsNotNone(message.published_at)
        with self.assertRaises(ValueError):
            publish_broadcast(message)


class TranslationTests(TestCase):
    @override_settings(GOOGLE_TRANSLATE_API_KEY="test-key")
    @patch("chat.utils.requests.post")
    def test_translation_forwards_supported_language(self, post):
        post.return_value = Mock(
            status_code=200,
            json=lambda: {"data": {"translations": [{"translatedText": "Wasuze otya"}]}},
        )

        translated = translate_message("Good morning", "lg")

        self.assertEqual(translated, "Wasuze otya")
        self.assertEqual(post.call_args.kwargs["json"]["target"], "lg")
