from rest_framework import viewsets

from utils.drf_http_permission import ReadOnlyModelViewSet
from .models import Notification
from .serializers import NotificationSerializer

class NotificationViewSet(ReadOnlyModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer