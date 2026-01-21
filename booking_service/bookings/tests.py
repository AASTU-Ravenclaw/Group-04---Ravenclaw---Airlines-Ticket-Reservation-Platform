import uuid
import datetime
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from unittest.mock import patch, Mock
from rest_framework import status
from rest_framework.test import APITestCase

from bookings.models import Booking, Passenger
from bookings.serializers import BookingSerializer, PassengerSerializer
from django.conf import settings


class BookingModelTests(TestCase):
	def test_booking_str(self):
		booking = Booking.objects.create(user_id=uuid.uuid4(), flight_id=uuid.uuid4())
		self.assertIn(str(booking.booking_id), str(booking))
		self.assertIn("Booking", str(booking))


class BookingSerializerTests(TestCase):
	def setUp(self):
		self.user_id = uuid.uuid4()
		self.flight_id = uuid.uuid4()

	def test_create_with_explicit_passengers_list(self):
		data = {
			"flight_id": self.flight_id,
			"passengers": 2,
			"passengers_list": [
				{"first_name": "Ada", "last_name": "Lovelace", "email": "ada@example.com"},
				{"first_name": "Alan", "last_name": "Turing", "email": "alan@example.com"},
			],
			"user_id": self.user_id,
		}
		serializer = BookingSerializer(data=data)
		self.assertTrue(serializer.is_valid(), serializer.errors)
		booking = serializer.save(user_id=self.user_id)
		self.assertEqual(booking.user_id, self.user_id)
		self.assertEqual(booking.flight_id, self.flight_id)
		self.assertEqual(booking.passengers.count(), 2)
		names = {(p.first_name, p.last_name) for p in booking.passengers.all()}
		self.assertIn(("Ada", "Lovelace"), names)
		self.assertIn(("Alan", "Turing"), names)

	def test_create_with_passenger_count_defaults(self):
		data = {
			"flight_id": self.flight_id,
			"passengers": 3,
			"user_id": self.user_id,
		}
		serializer = BookingSerializer(data=data)
		self.assertTrue(serializer.is_valid(), serializer.errors)
		booking = serializer.save(user_id=self.user_id)
		self.assertEqual(booking.passengers.count(), 3)
		emails = {p.email for p in booking.passengers.all()}
		self.assertIn("passenger1@example.com", emails)
		self.assertIn("passenger2@example.com", emails)
		self.assertIn("passenger3@example.com", emails)


class BookingAPITests(APITestCase):
	def setUp(self):
		self.list_url = reverse("booking-list")
		self.user_id = uuid.uuid4()
		self.other_user_id = uuid.uuid4()
		self.flight_id = uuid.uuid4()

	def _headers(self, role="CLIENT", user_id=None, email="user@example.com"):
		return {
			"HTTP_X_USER_ID": str(user_id or self.user_id),
			"HTTP_X_USER_EMAIL": email,
			"HTTP_X_USER_ROLE": role,
		}

	def test_queryset_filters_by_role(self):
		# Create bookings for two users
		Booking.objects.create(user_id=self.user_id, flight_id=self.flight_id)
		Booking.objects.create(user_id=self.other_user_id, flight_id=self.flight_id)

		# Client sees only their bookings
		res_client = self.client.get(self.list_url, **self._headers(role="CLIENT", user_id=self.user_id))
		self.assertEqual(res_client.status_code, status.HTTP_200_OK)
		self.assertEqual(len(res_client.json()), 1)

		# Admin sees all bookings
		res_admin = self.client.get(self.list_url, **self._headers(role="ADMIN", user_id=self.user_id))
		self.assertEqual(res_admin.status_code, status.HTTP_200_OK)
		self.assertEqual(len(res_admin.json()), 2)

	@patch("bookings.views.publish_event")
	@patch("bookings.views.requests.post")
	def test_create_booking_success(self, mock_post, mock_publish):
		mock_post.return_value = Mock(status_code=200, text="OK")
		data = {
			"flight_id": str(self.flight_id),
			"passengers": 2,
			"passengers_list": [
				{"first_name": "Ada", "last_name": "Lovelace", "email": "ada@example.com"},
				{"first_name": "Alan", "last_name": "Turing", "email": "alan@example.com"},
			],
		}
		res = self.client.post(self.list_url, data, format="json", **self._headers(role="CLIENT"))
		self.assertEqual(res.status_code, status.HTTP_201_CREATED, res.data)
		self.assertEqual(Booking.objects.count(), 1)
		booking = Booking.objects.first()
		self.assertEqual(booking.user_id, self.user_id)
		# Two seat reservations were attempted
		self.assertEqual(mock_post.call_count, 2)
		expected_url = f"{settings.FLIGHT_SERVICE_URL}/api/v1/flights/{self.flight_id}/reserve_seat/"
		called_urls = [call.args[0] for call in mock_post.call_args_list]
		self.assertTrue(all(url == expected_url for url in called_urls))
		mock_publish.assert_called_once()

	@patch("bookings.views.publish_event")
	@patch("bookings.views.requests.post")
	def test_create_booking_reserve_failure(self, mock_post, mock_publish):
		mock_post.return_value = Mock(status_code=409, text="Full")
		data = {"flight_id": str(self.flight_id), "passengers": 1}
		res = self.client.post(self.list_url, data, format="json", **self._headers(role="CLIENT"))
		self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)
		self.assertEqual(Booking.objects.count(), 0)
		mock_publish.assert_not_called()

	@patch("bookings.views.publish_event")
	@patch("bookings.views.requests.post")
	@patch("bookings.views.requests.get")
	def test_cancel_booking_before_departure(self, mock_get, mock_post, mock_publish):
		booking = Booking.objects.create(user_id=self.user_id, flight_id=self.flight_id)
		Passenger.objects.create(booking=booking, first_name="Test", last_name="User", email="t@example.com")

		future_departure = (timezone.now() + timezone.timedelta(hours=2)).isoformat()
		mock_get.return_value = Mock(status_code=200, json=lambda: {"departure_time": future_departure})
		mock_post.return_value = Mock(status_code=200, text="Released")

		url = reverse("booking-detail", args=[booking.booking_id])
		res = self.client.delete(url, **self._headers(role="CLIENT"))
		self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)
		booking.refresh_from_db()
		self.assertEqual(booking.status, "CANCELLED")
		# Release called once for the passenger
		expected_release_url = f"{settings.FLIGHT_SERVICE_URL}/{booking.flight_id}/release_seat/"
		mock_post.assert_called_with(expected_release_url, headers={'X-Service-API-Key': settings.SERVICE_API_KEY})
		mock_publish.assert_called_once()

	@patch("bookings.views.requests.get")
	def test_cancel_booking_after_departure_blocked(self, mock_get):
		booking = Booking.objects.create(user_id=self.user_id, flight_id=self.flight_id)
		past_departure = (timezone.now() - timezone.timedelta(hours=1)).isoformat()
		mock_get.return_value = Mock(status_code=200, json=lambda: {"departure_time": past_departure})

		url = reverse("booking-detail", args=[booking.booking_id])
		res = self.client.delete(url, **self._headers(role="CLIENT"))
		self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
		booking.refresh_from_db()
		self.assertEqual(booking.status, "CONFIRMED")

	def test_health_check(self):
		res = self.client.get("/health/")
		self.assertEqual(res.status_code, status.HTTP_200_OK)
		data = getattr(res, "data", None) or res.json()
		self.assertEqual(data.get("status"), "healthy")
