from rest_framework import serializers, viewsets
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['user', 'message', 'read', 'timestamp']
        read_only_fields = ['user', 'timestamp','message']
