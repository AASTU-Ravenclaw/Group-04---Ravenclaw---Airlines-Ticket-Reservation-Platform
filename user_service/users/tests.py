from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.serializers import UserRegistrationSerializer, UserProfileSerializer


class UserModelTests(TestCase):
	def setUp(self):
		self.User = get_user_model()

	def test_create_user_normalizes_email_and_hashes_password(self):
		user = self.User.objects.create_user(
			email="TestUser@Example.com",
			password="secret123",
			first_name="Test",
			last_name="User",
		)
		self.assertEqual(user.email, "testuser@example.com")
		self.assertTrue(user.check_password("secret123"))

	def test_create_user_requires_email(self):
		with self.assertRaisesMessage(ValueError, "Email is required"):
			self.User.objects.create_user(email=None, password="secret123")

	def test_create_superuser_flags_and_role(self):
		admin = self.User.objects.create_superuser(
			email="admin@example.com",
			password="adminpass",
			first_name="Admin",
			last_name="User",
		)
		self.assertTrue(admin.is_staff)
		self.assertTrue(admin.is_superuser)
		self.assertEqual(admin.role, "ADMIN")

	def test_save_lowercases_email(self):
		user = self.User(
			email="MiXeD@Email.Com",
			first_name="Mix",
			last_name="Case",
		)
		user.set_password("pass12345")
		user.save()
		self.assertEqual(user.email, "mixed@email.com")


class UserSerializerTests(TestCase):
	def setUp(self):
		self.User = get_user_model()

	def test_user_registration_serializer_creates_user(self):
		data = {
			"first_name": "Jane",
			"last_name": "Doe",
			"email": "Jane.Doe@Email.com",
			"password": "mypassword",
		}
		serializer = UserRegistrationSerializer(data=data)
		self.assertTrue(serializer.is_valid(), serializer.errors)
		user = serializer.save()
		self.assertEqual(user.email, "jane.doe@email.com")
		self.assertTrue(user.check_password("mypassword"))
		self.assertEqual(user.role, "CLIENT")

	def test_user_profile_serializer_readonly_fields(self):
		user = self.User.objects.create_user(
			email="user@example.com",
			password="secret123",
			first_name="First",
			last_name="Last",
		)
		serializer = UserProfileSerializer(instance=user)
		data = serializer.data
		self.assertIn("email", data)
		self.assertIn("role", data)
		# Attempt to update read-only fields via serializer
		update = UserProfileSerializer(
			instance=user,
			data={"email": "new@example.com", "role": "ADMIN", "first_name": "New"},
			partial=True,
		)
		self.assertTrue(update.is_valid(), update.errors)
		updated = update.save()
		# Read-only fields should remain unchanged
		self.assertEqual(updated.email, "user@example.com")
		self.assertEqual(updated.role, "CLIENT")
		# Editable field changed
		self.assertEqual(updated.first_name, "New")


class UserAPITests(APITestCase):
	def setUp(self):
		self.register_url = reverse("register")
		self.login_url = reverse("login")
		self.refresh_url = reverse("token_refresh")
		self.profile_url = reverse("profile")
		self.validate_url = reverse("validate_token")
		# Use explicit users app health path to avoid name collision with root health
		self.health_url = "/api/v1/health/"

		self.user_data = {
			"first_name": "John",
			"last_name": "Doe",
			"email": "John.Doe@Email.com",
			"password": "password123",
		}

	def _register_and_login(self):
		# Register user
		reg_res = self.client.post(self.register_url, self.user_data, format="json")
		self.assertEqual(reg_res.status_code, status.HTTP_201_CREATED, reg_res.data)
		# Login
		login_res = self.client.post(
			self.login_url,
			{"email": self.user_data["email"], "password": self.user_data["password"]},
			format="json",
		)
		self.assertEqual(login_res.status_code, status.HTTP_200_OK, login_res.data)
		self.assertIn("access", login_res.data)
		self.assertIn("refresh", login_res.data)
		self.assertIn("user", login_res.data)
		return login_res.data

	def test_register_user(self):
		res = self.client.post(self.register_url, self.user_data, format="json")
		self.assertEqual(res.status_code, status.HTTP_201_CREATED, res.data)
		self.assertEqual(res.data["email"], "john.doe@email.com")
		self.assertNotIn("password", res.data)

	def test_login_returns_tokens_and_user_profile(self):
		tokens = self._register_and_login()
		self.assertEqual(tokens["user"]["email"], "john.doe@email.com")

	def test_refresh_token(self):
		tokens = self._register_and_login()
		res = self.client.post(self.refresh_url, {"refresh": tokens["refresh"]}, format="json")
		self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)
		self.assertIn("access", res.data)

	def test_get_and_update_profile(self):
		tokens = self._register_and_login()
		access = tokens["access"]
		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

		# Get profile
		res = self.client.get(self.profile_url)
		self.assertEqual(res.status_code, status.HTTP_200_OK)
		self.assertEqual(res.data["email"], "john.doe@email.com")

		# Update first_name (allowed)
		res = self.client.patch(self.profile_url, {"first_name": "Johnny"}, format="json")
		self.assertEqual(res.status_code, status.HTTP_200_OK)
		self.assertEqual(res.data["first_name"], "Johnny")

		# Attempt to update email (read-only)
		res = self.client.patch(self.profile_url, {"email": "new@example.com"}, format="json")
		self.assertEqual(res.status_code, status.HTTP_200_OK)
		self.assertEqual(res.data["email"], "john.doe@email.com")

	def test_validate_token_endpoint(self):
		tokens = self._register_and_login()
		access = tokens["access"]
		# validate token via header
		res = self.client.get(self.validate_url, HTTP_AUTHORIZATION=f"Bearer {access}")
		self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)
		self.assertTrue(res.data.get("valid"))
		self.assertEqual(res["X-User-Email"], "john.doe@email.com")
		self.assertEqual(res["X-User-Role"], "CLIENT")

	def test_validate_token_bad_header(self):
		res = self.client.get(self.validate_url, HTTP_AUTHORIZATION="Token abcdef")
		self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_health_check(self):
		# Root health check
		res_root = self.client.get(self.health_url)
		self.assertEqual(res_root.status_code, status.HTTP_200_OK)
		# DRF Response provides .data; if plain HttpResponse, fallback to content
		status_val = getattr(res_root, "data", None) or {"status": res_root.content.decode("utf-8").strip('"{}').split(": ")[-1]}
		self.assertEqual(status_val["status"], "healthy")
