from rest_framework import viewsets, permissions, generics,filters

from apps.proposals.models import Proposal, SubmissionsProposalApply
from apps.proposals.serializers import ProposalSerializer, SubmissionProposalApplySerializer, TagSerializer
from taggit.models import Tag
from apps.proposals.filter import ProposalFilter, SubmissionProposalApplyFilter
from django_filters.rest_framework import DjangoFilterBackend
# Create your views here.
class ProposalViewSet(viewsets.ModelViewSet):
    serializer_class = ProposalSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProposalFilter
    search_fields = ['title', 'team__name', 'tag__name']
    ordering_fields = ['created_at']

    def get_queryset(self):
        team_id = self.kwargs.get('team_id')
        return Proposal.objects.filter(team_id=team_id)

class TagListView(generics.ListAPIView):
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name']
    
    def get_queryset(self):
        return Tag.objects.filter(proposals__isnull=False).distinct()
    
class SubmissionProposalApplyViewSet(viewsets.ModelViewSet):
    serializer_class = SubmissionProposalApplySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = SubmissionProposalApplyFilter
    search_fields = ['submission__title', 'lecturer__user__email', 'status']
    ordering_fields = ['created_at']
    
    def get_queryset(self):
        team_id = self.kwargs.get('team_id')
        return SubmissionsProposalApply.objects.filter(team_id=team_id)
    