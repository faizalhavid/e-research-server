from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class BaseNotification:
    def __init__(self, user, message):
        self.user = user
        self.message = message
        self.group_name = f"user_{self.user.id}"
        self.channel_layer = get_channel_layer()

    def send_notification(self):
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                "type": "notification_message",
                "message": self.message,
            },
        )
        