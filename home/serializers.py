from rest_framework import serializers
from home.models import Device
from home.models import Log


class DeviceSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = Device
        fields = "__all__"


class AssistantCommandSerializer(serializers.Serializer):
    command = serializers.CharField(max_length=500)


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = "__all__"
