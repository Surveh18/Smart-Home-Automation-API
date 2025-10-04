from django.db import models
from django.contrib.auth.models import User

class Device(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    device_type = models.CharField(max_length=20)
    status = models.CharField(max_length=50, default="off")

    def __str__(self):
        return f"{self.name} ({self.device_type}) - {self.status}"

class Log(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)
    value = models.FloatField(null=True, blank=True)  # Optional field
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device.name} - {self.action} @ {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"