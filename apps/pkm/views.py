from rest_framework import generics, permissions, viewsets, mixins, filters

from apps.pkm.filter import PKMActivityScheduleFilter
from apps.pkm.models import PKMActivitySchedule, PKMScheme
from apps.pkm.serializers import PKMActivityScheduleSerializer, PKMSchemeSerializer
from django_filters.rest_framework import DjangoFilterBackend


class PKMSchemeList(generics.ListAPIView):
    queryset = PKMScheme.objects.all()
    serializer_class = PKMSchemeSerializer
    permission_classes = [permissions.IsAuthenticated]

class PKMActivityScheduleViewSet(mixins.RetrieveModelMixin,
                                 mixins.ListModelMixin,
                                 viewsets.GenericViewSet):
    queryset = PKMActivitySchedule.objects.all().order_by('start_date')
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PKMActivityScheduleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = PKMActivityScheduleFilter
    search_fields = ['title', 'description']