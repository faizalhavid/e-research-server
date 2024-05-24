from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from notification.models import Notification
from notification.serializers import NotificationSerializer

class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()
        notifications = await self.get_notifications()
        await self.send_json(notifications)

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        notifications = await self.get_notifications()
        await self.send_json(notifications)

    @database_sync_to_async
    def get_notifications(self):
        notifications = Notification.objects.all()
        serializer = NotificationSerializer(notifications, many=True)
        return serializer.data