from django.shortcuts import get_object_or_404
from requests import Response
from rest_framework import permissions, viewsets,filters,views,mixins

from apps.pkm.filter import PKMActivityScheduleFilter
from apps.pkm.models import PKMActivitySchedule, PKMIdeaContribute, PKMIdeaContributeApplyTeam, PKMScheme
from apps.pkm.serializers import PKMActivityScheduleSerializer, PKMIdeaContributeApplyTeamSerializer, PKMIdeaContributeSerializer, PKMSchemeSerializer
from django_filters.rest_framework import DjangoFilterBackend

from apps.team.models import Team
from rest_framework.pagination import PageNumberPagination
from utils.exceptions import success_response
from django.db.models import Q
from rest_framework.decorators import action


class PKMSchemeList(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = PKMScheme.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PKMSchemeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'abbreviation', 'description']

class PKMActivityScheduleViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
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
    # queryset = PKMIdeaContribute.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PKMIdeaContributeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['title', 'tags__name', 'description']
    ordering_fields = ['created']
    lookup_field = 'slug'
    def get_queryset(self):
        return PKMIdeaContribute.objects.filter(status='P')

    @action(detail=False, methods=['get'])
    def by_user(self, request, *args, **kwargs):
        user_contributions = PKMIdeaContribute.objects.filter(user=request.user, status='P')
        serializer = self.get_serializer(user_contributions, many=True)
        return success_response('Idea Contribute by User', serializer.data)
    
class IdeaContributeReportView(views.APIView):
    def get(self, request):
        user = request.user

        user_contributions = PKMIdeaContribute.objects.filter(user=user)

        total_contributions = user_contributions.count()
        published_contributions = user_contributions.filter(status='P').count()
        contributions_with_team = sum(contribution.apply_teams.exists() for contribution in user_contributions)

        tags = []
        for contribution in user_contributions:
            for tag in contribution.tags.all():
                if tag.name not in tags:
                    tags.append(tag.name)

        tags = ', '.join(tags)


        return success_response(
            message="Idea Contribute Report",
            data={
                'total_contributions': total_contributions,
                'published_contributions': published_contributions,
                'contributions_with_team': contributions_with_team,
                'tags': tags
            },
            status_code=200
        )
    


class PKMIdeaContributeApplyTeamViewSet(viewsets.ModelViewSet):
    serializer_class = PKMIdeaContributeApplyTeamSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['team__name', 'idea_contribute__title', 'status']
    filterset_fields = ['team__slug', 'idea_contribute__user', 'status']
    lookup_field = 'idea_contributed_slug'
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return PKMIdeaContributeApplyTeam.objects.all()
        if PKMIdeaContributeApplyTeam.objects.filter(idea_contribute__user=user).exists():
            return PKMIdeaContributeApplyTeam.objects.filter(idea_contribute__user=user)
        
        return PKMIdeaContributeApplyTeam.objects.filter(Q(team__leader=user) | Q(team__members=user))
