from django.shortcuts import redirect, render
from requests import Response
from rest_framework import viewsets, permissions, generics,filters,mixins

from apps.proposals.form import AssignLecturerForm
from apps.proposals.models import  AssesmentSubmissionsProposal, SubmissionProposal, SubmissionsProposalApply
from apps.proposals.serializers import SubmissionProposalApplySerializer, SubmissionProposalSerializer, TagSerializer
from taggit.models import Tag
from apps.proposals.filter import  SubmissionProposalApplyFilter, TagFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django.contrib import messages
from utils.exceptions import success_response



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
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TagFilter  # Corrected from filter_class to filterset_class
    search_fields = ['name']
    queryset = Tag.objects.all()
    
class SubmissionProposalApplyViewSet(viewsets.ModelViewSet):
    serializer_class = SubmissionProposalApplySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = SubmissionProposalApplyFilter
    search_fields = ['submission__title', 'lecturer__user__email', 'status']
    ordering_fields = ['created_at']
    queryset = SubmissionsProposalApply.objects.all()
    lookup_field = 'slug'
    
    
    @action(detail=False, methods=['get'], url_path='by_team/(?P<team_slug>[^/.]+)')
    def by_team(self, request, *args, **kwargs):
        team_slug = kwargs.get('team_slug')
        
        if not team_slug:
            return success_response('Team id is required')
        queryset = SubmissionsProposalApply.objects.filter(team__slug=team_slug)
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = self.get_serializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
