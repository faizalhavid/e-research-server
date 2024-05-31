from rest_framework import viewsets, permissions, generics,filters,mixins

from apps.proposals.models import  SubmissionProposal, SubmissionsProposalApply
from apps.proposals.serializers import SubmissionProposalApplySerializer, SubmissionProposalSerializer, TagSerializer
from taggit.models import Tag
from apps.proposals.filter import  SubmissionProposalApplyFilter
from django_filters.rest_framework import DjangoFilterBackend


# class ProposalViewSet(viewsets.ModelViewSet):
#     serializer_class = ProposalSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
#     filterset_class = ProposalFilter
#     search_fields = ['title', 'team__name', 'tag__name']
#     ordering_fields = ['created_at']

#     def get_queryset(self):
#         team_id = self.kwargs.get('team_id')
#         return Proposal.objects.filter(team_id=team_id)


class SubmissionProposalViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = SubmissionProposal.objects.all().order_by('-created_at')
    serializer_class = SubmissionProposalSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at']
    lookup_field = 'slug'

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
    