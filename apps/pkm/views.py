from rest_framework import generics, permissions, viewsets, mixins, filters

from apps.pkm.filter import PKMActivityScheduleFilter
from apps.pkm.models import PKMActivitySchedule, PKMIdeaContribute, PKMScheme
from apps.pkm.serializers import PKMActivityScheduleSerializer, PKMIdeaContributeSerializer, PKMSchemeSerializer
from django_filters.rest_framework import DjangoFilterBackend

from utils.drf_http_permission import ReadOnlyModelViewSet


class PKMSchemeList(ReadOnlyModelViewSet):
    queryset = PKMScheme.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PKMSchemeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'abbreviation', 'description']

class PKMActivityScheduleViewSet(ReadOnlyModelViewSet):
    queryset = PKMActivitySchedule.objects.all().order_by('start_date')
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PKMActivityScheduleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = PKMActivityScheduleFilter
    search_fields = ['title', 'description']

class PKMIdeaContributeViewSet(viewsets.ModelViewSet):
    queryset = PKMActivitySchedule.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PKMActivityScheduleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['title', 'description']

    def get_queryset(self):
        return PKMActivitySchedule.objects.filter(title='PKM Idea Contribute')


class PKMIdeaContributeViewSet(viewsets.ModelViewSet):
    queryset = PKMIdeaContribute.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PKMIdeaContributeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['title', 'tags__name', 'description']
    ordering_fields = ['created']

    def get_queryset(self):
        return PKMIdeaContribute.objects.filter(status='published')
    
