"""
Unit Tests for Smart Home API
File: home/tests.py

Run tests:
    python manage.py test home.tests
    python manage.py test home.tests --verbosity=2
    python manage.py test home.tests.AuthenticationTests
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from home.models import Device, Log
import json


# ========================================
# 1. AUTHENTICATION TESTS
# ========================================


class AuthenticationTests(APITestCase):
    """Test JWT authentication flow"""

    def setUp(self):
        """Create test user"""
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )
        self.client = APIClient()

    def test_login_success(self):
        """Test: Valid credentials give access and refresh tokens"""
        url = "/api/token/"
        data = {"username": "testuser", "password": "testpass123"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        print("✅ Login successful - tokens received")

    def test_login_invalid_credentials(self):
        """Test: Invalid credentials return 401"""
        url = "/api/token/"
        data = {"username": "testuser", "password": "wrongpassword"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        print("✅ Invalid credentials rejected")

    def test_token_refresh(self):
        """Test: Refresh token generates new access token"""
        # Get initial tokens
        url = "/api/token/"
        data = {"username": "testuser", "password": "testpass123"}
        response = self.client.post(url, data, format="json")
        refresh_token = response.data["refresh"]

        # Refresh token
        refresh_url = "/api/token/refresh/"
        refresh_data = {"refresh": refresh_token}
        refresh_response = self.client.post(refresh_url, refresh_data, format="json")

        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_response.data)
        print("✅ Token refreshed successfully")

    def test_unauthorized_access(self):
        """Test: API requires authentication"""
        url = "/api/devices/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        print("✅ Unauthorized access blocked")


# ========================================
# 2. DEVICE CRUD TESTS
# ========================================


class DeviceCRUDTests(APITestCase):
    """Test Device Create, Read, Update, Delete operations"""

    def setUp(self):
        """Setup authenticated client"""
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.client = APIClient()

        # Get token and authenticate
        url = "/api/token/"
        data = {"username": "testuser", "password": "testpass123"}
        response = self.client.post(url, data, format="json")
        self.token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_create_device(self):
        """Test: Create new device"""
        url = "/api/devices/"
        data = {"name": "Living Room Light", "device_type": "light", "status": "off"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Living Room Light")
        self.assertEqual(response.data["device_type"], "light")
        self.assertEqual(Device.objects.count(), 1)
        print(f"✅ Device created: {response.data['name']}")

    def test_list_devices(self):
        """Test: List all user devices"""
        # Create test devices
        Device.objects.create(
            name="Light 1", device_type="light", status="off", user=self.user
        )
        Device.objects.create(
            name="Light 2", device_type="light", status="on", user=self.user
        )

        url = "/api/devices/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        print(f"✅ Listed {len(response.data)} devices")

    def test_get_single_device(self):
        """Test: Get specific device details"""
        device = Device.objects.create(
            name="Test Light", device_type="light", status="off", user=self.user
        )

        url = f"/api/devices/{device.id}/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Light")
        print(f"✅ Retrieved device: {response.data['name']}")

    def test_update_device(self):
        """Test: Update device (PUT)"""
        device = Device.objects.create(
            name="Old Name", device_type="light", status="off", user=self.user
        )

        url = f"/api/devices/{device.id}/"
        data = {"name": "New Name", "device_type": "light", "status": "on"}
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "New Name")
        self.assertEqual(response.data["status"], "on")
        print(f"✅ Device updated: {response.data['name']}")

    def test_partial_update_device(self):
        """Test: Partial update device (PATCH)"""
        device = Device.objects.create(
            name="Test Light", device_type="light", status="off", user=self.user
        )

        url = f"/api/devices/{device.id}/"
        data = {"status": "on"}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "on")
        self.assertEqual(response.data["name"], "Test Light")  # Unchanged
        print("✅ Device partially updated")

    def test_delete_device(self):
        """Test: Delete device"""
        device = Device.objects.create(
            name="To Delete", device_type="light", status="off", user=self.user
        )

        url = f"/api/devices/{device.id}/"
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Device.objects.count(), 0)
        print("✅ Device deleted")

    def test_user_isolation(self):
        """Test: Users can only see their own devices"""
        # Create another user
        other_user = User.objects.create_user(
            username="otheruser", password="otherpass123"
        )

        # Create device for other user
        Device.objects.create(
            name="Other User Device", device_type="light", status="off", user=other_user
        )

        # Create device for current user
        Device.objects.create(
            name="My Device", device_type="light", status="off", user=self.user
        )

        url = "/api/devices/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "My Device")
        print("✅ User isolation working")


# ========================================
# 3. DEVICE CONTROL TESTS
# ========================================


class DeviceControlTests(APITestCase):
    """Test device control actions (turn on/off, set temperature)"""

    def setUp(self):
        """Setup authenticated client and test device"""
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.client = APIClient()

        # Get token
        url = "/api/token/"
        data = {"username": "testuser", "password": "testpass123"}
        response = self.client.post(url, data, format="json")
        self.token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        # Create test device
        self.device = Device.objects.create(
            name="Test Light", device_type="light", status="off", user=self.user
        )

    def test_turn_on_device(self):
        """Test: Turn on device"""
        url = f"/api/devices/{self.device.id}/control/"
        data = {"action": "turn_on"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.device.refresh_from_db()
        self.assertEqual(self.device.status, "on")
        print(f"✅ Device turned on: {self.device.name}")

    def test_turn_off_device(self):
        """Test: Turn off device"""
        self.device.status = "on"
        self.device.save()

        url = f"/api/devices/{self.device.id}/control/"
        data = {"action": "turn_off"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.device.refresh_from_db()
        self.assertEqual(self.device.status, "off")
        print(f"✅ Device turned off: {self.device.name}")

    def test_set_temperature_valid(self):
        """Test: Set temperature within valid range"""
        thermostat = Device.objects.create(
            name="Thermostat", device_type="thermostat", status="22", user=self.user
        )

        url = f"/api/devices/{thermostat.id}/control/"
        data = {"action": "set_temperature", "value": 25}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        thermostat.refresh_from_db()
        self.assertEqual(thermostat.status, "25")
        print(f"✅ Temperature set to: {thermostat.status}")

    def test_set_temperature_invalid_too_low(self):
        """Test: Temperature below minimum should fail"""
        ac = Device.objects.create(
            name="AC", device_type="ac", status="24", user=self.user
        )

        url = f"/api/devices/{ac.id}/control/"
        data = {"action": "set_temperature", "value": 10}  # Below minimum (16)
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        print(f"✅ Invalid temperature rejected: {response.data['error']}")

    def test_set_temperature_invalid_too_high(self):
        """Test: Temperature above maximum should fail"""
        ac = Device.objects.create(
            name="AC", device_type="ac", status="24", user=self.user
        )

        url = f"/api/devices/{ac.id}/control/"
        data = {"action": "set_temperature", "value": 50}  # Above maximum (30)
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print(f"✅ Invalid temperature rejected")

    def test_invalid_action(self):
        """Test: Invalid action returns error"""
        url = f"/api/devices/{self.device.id}/control/"
        data = {"action": "fly_to_moon"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print("✅ Invalid action rejected")


# ========================================
# 4. ASSISTANT COMMAND TESTS
# ========================================


class AssistantCommandTests(APITestCase):
    """Test Gemini assistant command parsing"""

    def setUp(self):
        """Setup authenticated client and devices"""
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.client = APIClient()

        # Get token
        url = "/api/token/"
        data = {"username": "testuser", "password": "testpass123"}
        response = self.client.post(url, data, format="json")
        self.token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        # Create test devices
        self.light = Device.objects.create(
            name="Living Room Light", device_type="light", status="off", user=self.user
        )

        self.thermostat = Device.objects.create(
            name="Thermostat", device_type="thermostat", status="22", user=self.user
        )

    def test_missing_command(self):
        """Test: Missing command returns error"""
        url = "/api/assistant/command/"
        data = {}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        print("✅ Missing command error handled")

    def test_device_not_found(self):
        """Test: Non-existent device returns 404"""
        url = "/api/assistant/command/"
        data = {"command": "turn on the kitchen light"}
        response = self.client.post(url, data, format="json")

        # This test depends on Gemini parsing
        # It might return 404 or 400 based on Gemini response
        self.assertIn(
            response.status_code,
            [status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST],
        )
        print(f"Response: {response.status_code} - Command processed")


# ========================================
# 5. LOG TESTS
# ========================================


class LogTests(APITestCase):
    """Test activity logging"""

    def setUp(self):
        """Setup authenticated client"""
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.client = APIClient()

        # Get token
        url = "/api/token/"
        data = {"username": "testuser", "password": "testpass123"}
        response = self.client.post(url, data, format="json")
        self.token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        # Create device
        self.device = Device.objects.create(
            name="Test Light", device_type="light", status="off", user=self.user
        )

    def test_view_logs(self):
        """Test: Can view logs"""
        # Create log entry
        Log.objects.create(device_id=self.device.id, action="turn_on", value=None)

        url = "/api/logs/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        print(f"✅ Found {len(response.data)} log(s)")

    def test_log_created_after_action(self):
        """Test: Log is created after device action"""
        initial_log_count = Log.objects.count()

        # Perform action
        url = f"/api/devices/{self.device.id}/control/"
        data = {"action": "turn_on"}
        self.client.post(url, data, format="json")

        final_log_count = Log.objects.count()
        self.assertEqual(final_log_count, initial_log_count + 1)
        print("✅ Log created after device action")


# ========================================
# 6. LOGOUT TESTS
# ========================================


class LogoutTests(APITestCase):
    """Test logout functionality"""

    def setUp(self):
        """Setup user and tokens"""
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.client = APIClient()

        # Get tokens
        url = "/api/token/"
        data = {"username": "testuser", "password": "testpass123"}
        response = self.client.post(url, data, format="json")
        self.access_token = response.data["access"]
        self.refresh_token = response.data["refresh"]

    def test_logout_success(self):
        """Test: Logout blacklists refresh token"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        url = "/api/logout/"
        data = {"refresh": self.refresh_token}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        print("✅ Logout successful")

    def test_logout_missing_refresh_token(self):
        """Test: Logout without refresh token returns error"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        url = "/api/logout/"
        data = {}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print("✅ Missing refresh token error handled")


# ========================================
# RUN ALL TESTS
# ========================================

"""
To run all tests:
    python manage.py test home.tests

To run specific test class:
    python manage.py test home.tests.AuthenticationTests

To run with coverage:
    pip install coverage
    coverage run --source='.' manage.py test home.tests
    coverage report
    coverage html
"""
