from rest_framework import viewsets,mixins

from .models import Notification
from .serializers import NotificationDetailSerializer, NotificationListSerializer

from rest_framework import viewsets, mixins

class NotificationViewSet(viewsets.GenericViewSet, mixins.UpdateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    ordering_fields = ['timestamp']
    search_fields = ['message']
    filterset_fields = ['read']
    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Notification.objects.all()
        return Notification.objects.filter(user=user)
    
    def perform_update(self, serializer):
        serializer.save(read=True)

    def get_serializer_class(self):
        if self.action == 'list':
            return NotificationListSerializer
        else:
            return NotificationDetailSerializer
        
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not request.user.is_superuser:
            instance.read = True
            instance.save(update_fields=['read'])
        return super().retrieve(request, *args, **kwargs)