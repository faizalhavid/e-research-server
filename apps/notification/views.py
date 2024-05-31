from rest_framework import viewsets,mixins

from .models import Notification
from .serializers import NotificationSerializer

class NotificationViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin):
    serializer_class = NotificationSerializer
    ordering_fields = ['timestamp']
    search_fields = ['message']
    filterset_fields = ['read']
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(read=True)
