from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone
from unittest.mock import patch

from django.conf import settings

from .models import Location, Flight
from .serializers import (
	LocationSerializer,
	FlightCreateSerializer,
	FlightReadSerializer,
	FlightUpdateSerializer,
)


class LocationModelTests(TestCase):
	def test_location_str(self):
		loc = Location.objects.create(
			name="John F. Kennedy International",
			airport_code="JFK",
			city="New York",
			country="USA",
		)
		self.assertEqual(str(loc), "JFK - John F. Kennedy International")


class FlightSerializerTests(TestCase):
	def setUp(self):
		self.origin = Location.objects.create(name="JFK Airport", airport_code="JFK", city="New York", country="USA")
		self.dest = Location.objects.create(name="LAX Airport", airport_code="LAX", city="Los Angeles", country="USA")

	def test_flight_create_serializer_valid(self):
		departure = timezone.now() + timezone.timedelta(days=1)
		arrival = departure + timezone.timedelta(hours=6)
		data = {
			"flight_number": "AA100",
			"departure_location": "JFK",
			"arrival_location": "LAX",
			"departure_time": departure,
			"arrival_time": arrival,
			"total_seats": 200,
			"available_seats": 200,
			"price": "199.99",
		}
		serializer = FlightCreateSerializer(data=data)
		self.assertTrue(serializer.is_valid(), serializer.errors)
		flight = serializer.save()
		self.assertEqual(flight.departure_location, self.origin)
		self.assertEqual(flight.arrival_location, self.dest)
		self.assertEqual(flight.status, "scheduled")

	def test_flight_create_serializer_same_locations_invalid(self):
		departure = timezone.now() + timezone.timedelta(days=1)
		arrival = departure + timezone.timedelta(hours=6)
		data = {
			"flight_number": "AA200",
			"departure_location": "JFK",
			"arrival_location": "JFK",
			"departure_time": departure,
			"arrival_time": arrival,
			"total_seats": 100,
			"available_seats": 100,
			"price": "99.99",
		}
		serializer = FlightCreateSerializer(data=data)
		self.assertFalse(serializer.is_valid())
		self.assertIn("Departure and Arrival locations cannot be the same.", str(serializer.errors))

	def test_flight_create_serializer_seats_invalid(self):
		departure = timezone.now() + timezone.timedelta(days=1)
		arrival = departure + timezone.timedelta(hours=2)
		data = {
			"flight_number": "AA300",
			"departure_location": "JFK",
			"arrival_location": "LAX",
			"departure_time": departure,
			"arrival_time": arrival,
			"total_seats": 100,
			"available_seats": 150,
			"price": "120.00",
		}
		serializer = FlightCreateSerializer(data=data)
		self.assertFalse(serializer.is_valid())
		self.assertIn("Available seats cannot exceed total seats.", str(serializer.errors))

	def test_flight_create_serializer_times_invalid(self):
		departure = timezone.now() + timezone.timedelta(days=1)
		arrival = departure - timezone.timedelta(hours=1)
		data = {
			"flight_number": "AA400",
			"departure_location": "JFK",
			"arrival_location": "LAX",
			"departure_time": departure,
			"arrival_time": arrival,
			"total_seats": 100,
			"available_seats": 100,
			"price": "120.00",
		}
		serializer = FlightCreateSerializer(data=data)
		self.assertFalse(serializer.is_valid())
		self.assertIn("Arrival time must be after departure time.", str(serializer.errors))

	def test_flight_update_serializer_delay_and_events(self):
		departure = timezone.now() + timezone.timedelta(days=1)
		arrival = departure + timezone.timedelta(hours=2)
		flight = Flight.objects.create(
			flight_number="AA500",
			departure_location=self.origin,
			arrival_location=self.dest,
			departure_time=departure,
			arrival_time=arrival,
			total_seats=100,
			available_seats=100,
			price="150.00",
		)

		new_departure = departure + timezone.timedelta(hours=1)
		with patch("flights.serializers.publish_event") as mock_publish:
			serializer = FlightUpdateSerializer(instance=flight, data={"departure_time": new_departure}, partial=True)
			self.assertTrue(serializer.is_valid(), serializer.errors)
			updated = serializer.save()
			self.assertEqual(updated.status, "delayed")
			mock_publish.assert_called()

	def test_flight_update_serializer_no_edit_after_departed(self):
		departure = timezone.now() + timezone.timedelta(days=1)
		arrival = departure + timezone.timedelta(hours=2)
		flight = Flight.objects.create(
			flight_number="AA600",
			departure_location=self.origin,
			arrival_location=self.dest,
			departure_time=departure,
			arrival_time=arrival,
			total_seats=100,
			available_seats=100,
			price="180.00",
			status="departed",
		)
		serializer = FlightUpdateSerializer(instance=flight, data={"status": "cancelled"}, partial=True)
		self.assertFalse(serializer.is_valid())
		self.assertIn("Cannot edit a flight that has departed.", str(serializer.errors))


class FlightAPITests(APITestCase):
	def setUp(self):
		self.location_list_url = reverse("location-list")
		self.flight_list_url = reverse("flight-list")
		self.origin = Location.objects.create(name="JFK Airport", airport_code="JFK", city="New York", country="USA")
		self.dest = Location.objects.create(name="LAX Airport", airport_code="LAX", city="Los Angeles", country="USA")

	def _admin_headers(self):
		return {
			"HTTP_X_USER_ID": "123",
			"HTTP_X_USER_EMAIL": "admin@example.com",
			"HTTP_X_USER_ROLE": "ADMIN",
		}

	def _client_headers(self):
		return {
			"HTTP_X_USER_ID": "456",
			"HTTP_X_USER_EMAIL": "client@example.com",
			"HTTP_X_USER_ROLE": "CLIENT",
		}

	def test_location_delete_blocked_when_in_use(self):
		# Create flight using origin location
		flight = Flight.objects.create(
			flight_number="AA700",
			departure_location=self.origin,
			arrival_location=self.dest,
			departure_time=timezone.now() + timezone.timedelta(days=1),
			arrival_time=timezone.now() + timezone.timedelta(days=1, hours=2),
			total_seats=100,
			available_seats=100,
			price="120.00",
		)
		# Attempt to delete origin location
		url = reverse("location-detail", args=[self.origin.location_id])
		res = self.client.delete(url, **self._admin_headers())
		self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn("Cannot delete location", str(res.data))

	def test_flight_create_requires_admin(self):
		data = {
			"flight_number": "AA800",
			"departure_location": "JFK",
			"arrival_location": "LAX",
			"departure_time": timezone.now() + timezone.timedelta(days=2),
			"arrival_time": timezone.now() + timezone.timedelta(days=2, hours=6),
			"total_seats": 150,
			"available_seats": 150,
			"price": "199.99",
		}
		# As CLIENT -> 403
		res_client = self.client.post(self.flight_list_url, data, format="json", **self._client_headers())
		self.assertEqual(res_client.status_code, status.HTTP_403_FORBIDDEN)

		# As ADMIN -> 201
		res_admin = self.client.post(self.flight_list_url, data, format="json", **self._admin_headers())
		self.assertEqual(res_admin.status_code, status.HTTP_201_CREATED, res_admin.data)

	def test_flight_list_filters(self):
		# Create flights
		Flight.objects.create(
			flight_number="AA900",
			departure_location=self.origin,
			arrival_location=self.dest,
			departure_time=timezone.now() + timezone.timedelta(days=1),
			arrival_time=timezone.now() + timezone.timedelta(days=1, hours=6),
			total_seats=100,
			available_seats=100,
			price="100.00",
		)
		Flight.objects.create(
			flight_number="BB1000",
			departure_location=self.dest,
			arrival_location=self.origin,
			departure_time=timezone.now() + timezone.timedelta(days=2),
			arrival_time=timezone.now() + timezone.timedelta(days=2, hours=6),
			total_seats=100,
			available_seats=100,
			price="150.00",
		)

		# Filter by origin airport code
		res_origin = self.client.get(self.flight_list_url + "?origin=JFK")
		self.assertEqual(res_origin.status_code, status.HTTP_200_OK)
		self.assertTrue(all(f["departure_location"]["airport_code"].lower() == "jfk" for f in res_origin.json()))

		# Filter by destination city substring
		res_dest_city = self.client.get(self.flight_list_url + "?destination=Los")
		self.assertEqual(res_dest_city.status_code, status.HTTP_200_OK)
		self.assertTrue(len(res_dest_city.json()) >= 1)

		# Filter by date
		date_str = (timezone.now() + timezone.timedelta(days=1)).date().isoformat()
		res_date = self.client.get(self.flight_list_url + f"?date={date_str}")
		self.assertEqual(res_date.status_code, status.HTTP_200_OK)
		self.assertTrue(len(res_date.json()) >= 1)

	def test_reserve_and_release_seat_requires_service_key(self):
		flight = Flight.objects.create(
			flight_number="AA1100",
			departure_location=self.origin,
			arrival_location=self.dest,
			departure_time=timezone.now() + timezone.timedelta(days=1),
			arrival_time=timezone.now() + timezone.timedelta(days=1, hours=2),
			total_seats=2,
			available_seats=2,
			price="99.00",
		)
		reserve_url = reverse("flight-reserve-seat", args=[flight.flight_id])
		release_url = reverse("flight-release-seat", args=[flight.flight_id])

		# Missing API key -> 403
		res_no_key = self.client.post(reserve_url)
		self.assertEqual(res_no_key.status_code, status.HTTP_403_FORBIDDEN)

		# With API key -> reserve twice, then full
		headers = {"HTTP_X_SERVICE_API_KEY": settings.SERVICE_API_KEY}
		res1 = self.client.post(reserve_url, **headers)
		self.assertEqual(res1.status_code, status.HTTP_200_OK)
		self.assertEqual(res1.data["remaining_seats"], 1)

		res2 = self.client.post(reserve_url, **headers)
		self.assertEqual(res2.status_code, status.HTTP_200_OK)
		self.assertEqual(res2.data["remaining_seats"], 0)

		# Third attempt -> 409 Conflict
		res3 = self.client.post(reserve_url, **headers)
		self.assertEqual(res3.status_code, status.HTTP_409_CONFLICT)

		# Release seat -> remaining_seats becomes 1
		rel = self.client.post(release_url, **headers)
		self.assertEqual(rel.status_code, status.HTTP_200_OK)
		self.assertEqual(rel.data["remaining_seats"], 1)

	def test_health_check(self):
		res = self.client.get("/health/")
		self.assertEqual(res.status_code, status.HTTP_200_OK)
		# Accept both DRF Response and JsonResponse
		data = getattr(res, "data", None) or res.json()
		self.assertEqual(data.get("status"), "healthy")
