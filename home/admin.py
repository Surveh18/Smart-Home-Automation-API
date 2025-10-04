from django.contrib import admin
from home.models import Device, Log


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("name", "device_type", "status", "user")
    search_fields = ("name", "device_type", "user__username")
    list_filter = ("status", "device_type")


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ("device", "action", "value", "timestamp")
    list_filter = ("device__name", "action")
    search_fields = ("device__name", "device__user__username")
    ordering = ("-timestamp",)
