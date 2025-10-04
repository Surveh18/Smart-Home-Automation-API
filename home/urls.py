from django.urls import path, include
from rest_framework.routers import DefaultRouter
from home.views import DeviceViewSet, AssistantCommandView, LogViewSet, LogoutView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r"devices", DeviceViewSet, basename="device")
router.register(r"logs", LogViewSet, basename="log")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "assistant/command/", AssistantCommandView.as_view(), name="assistant-command"
    ),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
