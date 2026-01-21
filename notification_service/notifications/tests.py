import uuid
from types import SimpleNamespace
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import Mock, patch

from notifications.models import Notification


class NotificationModelTests(TestCase):
	def test_to_dict_contains_expected_fields(self):
		n = Notification(
			id="abc123",
			user_id="user-1",
			message="Hello",
			event_type="booking_created",
			is_read=False,
			timestamp="2024-01-01T00:00:00Z",
		)
		data = n.to_dict()
		self.assertEqual(data["id"], "abc123")
		self.assertEqual(data["user_id"], "user-1")
		self.assertEqual(data["message"], "Hello")
		self.assertEqual(data["event_type"], "booking_created")
		self.assertFalse(data["is_read"])
		self.assertEqual(data["timestamp"], "2024-01-01T00:00:00Z")


class NotificationAPITests(APITestCase):
	def setUp(self):
		self.user_id = "user-1"
		self.other_user = "user-2"
		self.list_url = f"/api/v1/notifications/{self.user_id}/"
		self.unread_url = f"/api/v1/notifications/{self.user_id}/unread-count/"
		self.health_url = "/health/"

	def _headers(self, user_id=None):
		return {"HTTP_X_USER_ID": user_id or self.user_id}

	def test_missing_auth_header_denied(self):
		res = self.client.get(self.list_url)
		self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

	def test_user_cannot_access_another_user(self):
		res = self.client.get(self.list_url, **self._headers(user_id=self.other_user))
		self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

	@patch("notifications.views.Notification")
	def test_list_notifications_success(self, mock_notification):
		notif = SimpleNamespace(
			id="n1",
			user_id=self.user_id,
			message="Hello",
			event_type="booking_created",
			is_read=False,
			timestamp="2024-01-01T00:00:00Z",
			to_dict=lambda: {
				"id": "n1",
				"user_id": self.user_id,
				"message": "Hello",
				"event_type": "booking_created",
				"is_read": False,
				"timestamp": "2024-01-01T00:00:00Z",
			},
		)
		mock_qs = [notif]
		mock_objects = Mock()
		mock_objects.order_by.return_value = mock_qs
		mock_notification.objects.return_value = mock_objects

		res = self.client.get(self.list_url, **self._headers())
		self.assertEqual(res.status_code, status.HTTP_200_OK)
		self.assertEqual(res.data["count"], 1)
		self.assertEqual(res.data["results"][0]["id"], "n1")

	@patch("notifications.views.Notification")
	def test_unread_count(self, mock_notification):
		mock_objects = Mock()
		mock_objects.count.return_value = 3
		mock_notification.objects.return_value = mock_objects

		res = self.client.get(self.unread_url, **self._headers())
		self.assertEqual(res.status_code, status.HTTP_200_OK)
		self.assertEqual(res.data["unread_count"], 3)

	@patch("notifications.views.Notification")
	def test_mark_read_success(self, mock_notification):
		notif = Mock()
		notif.user_id = self.user_id
		notif.is_read = False
		notif.to_dict.return_value = {
			"id": "n1",
			"user_id": self.user_id,
			"message": "Hello",
			"event_type": "booking_created",
			"is_read": True,
			"timestamp": "2024-01-01T00:00:00Z",
		}
		mock_notification.objects.get.return_value = notif

		res = self.client.patch(f"/api/v1/notifications/n1/read/", **self._headers())
		self.assertEqual(res.status_code, status.HTTP_200_OK)
		self.assertTrue(notif.is_read)
		notif.save.assert_called_once()

	@patch("notifications.views.Notification")
	def test_mark_read_not_found(self, mock_notification):
		class DoesNotExist(Exception):
			pass
		mock_notification.DoesNotExist = DoesNotExist
		mock_notification.objects.get.side_effect = DoesNotExist()

		res = self.client.patch(f"/api/v1/notifications/n1/read/", **self._headers())
		self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

	@patch("notifications.views.Notification")
	def test_mark_read_unauthorized_other_user(self, mock_notification):
		notif = Mock()
		notif.user_id = self.other_user
		mock_notification.objects.get.return_value = notif

		res = self.client.patch(f"/api/v1/notifications/n1/read/", **self._headers())
		self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

	def test_health_check(self):
		res = self.client.get(self.health_url)
		self.assertEqual(res.status_code, status.HTTP_200_OK)
		data = getattr(res, "data", None) or res.json()
		self.assertEqual(data.get("status"), "healthy")
