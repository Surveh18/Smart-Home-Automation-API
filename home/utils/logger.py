from home.models import Log, Device

def log_action(device_id, action, value=None):
    try:
        device = Device.objects.get(id=device_id)
        Log.objects.create(device=device, action=action, value=value)
        print(f"📝 Logged: {device.name} - {action} - {value}")
    except Device.DoesNotExist:
        print(f"⚠️ Device with ID {device_id} not found. Log skipped.")