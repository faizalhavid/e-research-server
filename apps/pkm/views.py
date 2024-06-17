from django.shortcuts import get_object_or_404
from requests import Response
from rest_framework import permissions, viewsets,filters,views,mixins

from apps.account.models import Student
from apps.pkm.filter import PKMActivityScheduleFilter, PKMIdeaContributeFilter
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
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PKMIdeaContributeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'tags__name', 'description']
    filterset_class = PKMIdeaContributeFilter
    ordering_fields = ['created', 'applied_date']
    lookup_field = 'slug'

    def get_queryset(self):          
        if self.request.user.is_superuser:
                return PKMIdeaContribute.objects.all()
        if self.action == 'list':
            return PKMIdeaContribute.objects.filter(status='P')
        elif self.action == 'retrieve':
            return PKMIdeaContribute.objects.all()
        else:
            return PKMIdeaContribute.objects.none()
        

    @action(detail=False, methods=['get'])
    def by_user(self, request, *args, **kwargs):
        user = request.user
        if not user:
            return PKMIdeaContribute.objects.none()
    
        if user.is_superuser:
            idea_contributes = PKMIdeaContribute.objects.all()
        else:
            idea_contributes = PKMIdeaContribute.objects.filter(user=user)

        # Apply pagination
        paginator = PageNumberPagination()
        paginator.page_size = 10  
        result_page = paginator.paginate_queryset(idea_contributes, request)
        serializer = PKMIdeaContributeSerializer(result_page, many=True)


        return paginator.get_paginated_response(serializer.data)


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
    lookup_field = 'slug'
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return PKMIdeaContributeApplyTeam.objects.all()
        student = get_object_or_404(Student, user=user)
        return PKMIdeaContributeApplyTeam.objects.filter(Q(team__leader=student))
        # if PKMIdeaContributeApplyTeam.objects.filter(idea_contribute__user=user).exists():
        #     return PKMIdeaContributeApplyTeam.objects.filter(idea_contribute__user=user)

    # @action(detail=False, url_path='apply-team/(?P<team_slug>[-\w]+)', methods=['get'])
    # def apply_team(self, request,  team_slug):
    #     team = get_object_or_404(Team, slug=team_slug)
    #     team_apply_ideas = PKMIdeaContributeApplyTeam.objects.filter(team=team)
    #     serializer = PKMIdeaContributeApplyTeamSerializer(team_apply_ideas, many=True)
    #     return success_response('Apply Team Idea Contribute', serializer.data)