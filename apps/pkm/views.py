from django.shortcuts import get_object_or_404
from requests import Response
from rest_framework import permissions, viewsets,filters,views,mixins

from apps.account.models import Student, User
from apps.pkm.filter import PKMActivityScheduleFilter, PKMIdeaContributeFilter
from apps.pkm.models import PKMActivitySchedule, PKMIdeaContribute, PKMIdeaContributeApplyTeam, PKMScheme
from apps.pkm.serializers import PKMActivityScheduleSerializer, PKMIdeaContributeApplyTeamSerializer, PKMIdeaContributeSerializer, PKMSchemeSerializer
from django_filters.rest_framework import DjangoFilterBackend

from apps.team.models import Team
from rest_framework.pagination import PageNumberPagination
from utils.exceptions import failure_response, success_response
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
    queryset = PKMIdeaContribute.objects.filter(status='P')

    # def get_queryset(self):          
    #     if self.request.user.is_superuser:
    #             return PKMIdeaContribute.objects.all()        
    #     if self.action == 'list':
    #         return PKMIdeaContribute.objects.filter(status='P')
    #     elif self.action == 'retrieve':
    #         slug = self.kwargs.get('slug')  
    #         return PKMIdeaContribute.objects.filter(slug=slug)
    #     else:
    #         return PKMIdeaContribute.objects.none()
        

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
        serializer = PKMIdeaContributeSerializer(result_page, many=True, context={'request': request})


        return paginator.get_paginated_response(serializer.data)


class IdeaContributeReportView(views.APIView):
    def get(self, request):
        user = request.user

        user_contributions = PKMIdeaContribute.objects.filter(user=user)

        total_contributions = user_contributions.count()
        published_contributions = user_contributions.filter(status='P').count()
        contributions_with_team = sum(contribution.apply_teams.filter(status='A').count() for contribution in user_contributions)

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
    
    @action(detail=False, methods=['get'], url_path='by_creator', url_name='by_creator')
    def by_creator(self, request):
        user = request.user
        if user.is_superuser:
            queryset = PKMIdeaContributeApplyTeam.objects.all()
        else:
            queryset = PKMIdeaContributeApplyTeam.objects.filter(Q(idea_contribute__user=user))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PKMIdeaContributeApplyTeamSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        # Serialize the queryset directly if not paginating
        serializer = PKMIdeaContributeApplyTeamSerializer(queryset, many=True, context={'request': request})        
        return Response(serializer.data)
    
    @action(detail=False, methods=['patch'], url_path='approve/(?P<slug>[-\w]+)', url_name='approve')
    def approve(self, request, slug):
        apply_team = get_object_or_404(PKMIdeaContributeApplyTeam, slug=slug)
        # Check if request.user is the owner or a superuser
        if request.user != apply_team.idea_contribute.user and not request.user.is_superuser:
            return failure_response('You do not have permission to perform this action.', status_code=403)
        apply_team.status = 'A'
        apply_team.save()
        return success_response('Apply Team Idea Contribute Approved')
    
    @action(detail=False, methods=['patch'], url_path='reject/(?P<slug>[-\w]+)', url_name='reject')
    def reject(self, request, slug):
        apply_team = get_object_or_404(PKMIdeaContributeApplyTeam, slug=slug)
        # Check if request.user is the owner or a superuser
        if request.user != apply_team.idea_contribute.user and not request.user.is_superuser:
            return failure_response('You do not have permission to perform this action.', status_code=403)
        apply_team.status = 'R'
        apply_team.save()
        return success_response('Apply Team Idea Contribute Rejected')