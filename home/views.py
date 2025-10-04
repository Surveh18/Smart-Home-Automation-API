from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet
import logging

from home.models import Device, Log
from home.serializers import DeviceSerializer, LogSerializer
from home.utils.logger import log_action
from home.utils.gemini import parse_command_with_gemini

logger = logging.getLogger(__name__)

# ========================================
# VALIDATION CONSTANTS (Real-world limits)
# ========================================

DEVICE_LIMITS = {
    "thermostat": {"min": 16, "max": 32, "unit": "°C"},  # 16°C minimum  # 32°C maximum
    "ac": {"min": 16, "max": 30, "unit": "°C"},  # 16°C minimum  # 30°C maximum
    "heater": {"min": 18, "max": 35, "unit": "°C"},  # 18°C minimum  # 35°C maximum
    "fan": {"min": 0, "max": 5, "unit": "speed"},  # Speed 0 (off)  # Speed 5 (max)
}


def validate_device_value(device, value):
    """
    Validate if the value is within acceptable range for the device type
    Returns: (is_valid, error_message)
    """
    device_type = device.device_type.lower()

    # Get limits for this device type
    if device_type in DEVICE_LIMITS:
        limits = DEVICE_LIMITS[device_type]
        min_val = limits["min"]
        max_val = limits["max"]
        unit = limits["unit"]

        try:
            value = float(value)
        except (ValueError, TypeError):
            return False, f"Invalid value: must be a number"

        if value < min_val or value > max_val:
            return (
                False,
                f"{device.name} {unit} must be between {min_val} and {max_val}",
            )

        return True, None

    # For unknown device types, allow any value
    return True, None


def apply_device_action(device, action, value=None):
    """
    Apply action to device with validation
    Returns: (success, error_message)
    """
    if action == "turn_on":
        device.status = "on"
        device.save()
        return True, None

    elif action == "turn_off":
        device.status = "off"
        device.save()
        return True, None

    elif action == "set_temperature" and value is not None:
        # Validate temperature range
        is_valid, error_msg = validate_device_value(device, value)
        if not is_valid:
            return False, error_msg

        device.status = str(value)
        device.save()
        return True, None

    elif action == "set_speed" and value is not None:
        # For fan speed control
        is_valid, error_msg = validate_device_value(device, value)
        if not is_valid:
            return False, error_msg

        device.status = str(value)
        device.save()
        return True, None

    else:
        return False, "Invalid action or missing value"


class LogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Log.objects.all().order_by("-timestamp")
    serializer_class = LogSerializer
    permission_classes = [IsAuthenticated]


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Device.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def control(self, request, pk=None):
        device = get_object_or_404(Device, pk=pk, user=request.user)
        action_type = request.data.get("action")
        value = request.data.get("value")

        # Apply action with validation
        success, error_msg = apply_device_action(device, action_type, value)

        if not success:
            return Response(
                {"error": error_msg},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Log the action
        log_action(device.id, action_type, value)

        return Response(
            {
                "message": f"{device.name} updated to {device.status}",
                "device": device.name,
                "new_status": device.status,
            },
            status=status.HTTP_200_OK,
        )


class AssistantCommandView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        command_text = request.data.get("command")
        if not command_text:
            return Response(
                {"error": "Missing command"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Parse command using Gemini
        parsed = parse_command_with_gemini(command_text)
        logger.info(f"Gemini parsed: {parsed}")

        if not parsed or "device_name" not in parsed or "action" not in parsed:
            return Response(
                {"error": "Could not understand command. Please try again."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        device_name = parsed["device_name"]
        action = parsed["action"]
        value = parsed.get("value")

        # Find device (case-insensitive, user-specific)
        device = Device.objects.filter(
            name__iexact=device_name, user=request.user
        ).first()

        if not device:
            return Response(
                {
                    "error": f"Device '{device_name}' not found",
                    "suggestion": "Please check device name or add it first",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Apply action with validation
        success, error_msg = apply_device_action(device, action, value)

        if not success:
            return Response(
                {"error": error_msg, "command": command_text, "device": device.name},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Log the action
        log_action(device.id, action, value)

        return Response(
            {
                "message": f"{device.name} updated successfully",
                "device": device.name,
                "action": action,
                "value": value if value else None,
                "new_status": device.status,
                "command_understood": command_text,
            },
            status=status.HTTP_200_OK,
        )


# ========================================
# LOGOUT VIEW (Optional - Alexa style)
# ========================================

from rest_framework_simplejwt.tokens import RefreshToken


class LogoutView(APIView):
    """
    Optional logout endpoint (Alexa-style).
    Devices stay connected until token expires.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")

            if not refresh_token:
                return Response(
                    {"error": "Refresh token required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {
                    "message": "Successfully logged out",
                    "note": "Your devices will remain connected until the current session expires",
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": f"Logout failed: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
