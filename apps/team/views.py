from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, filters, generics
from apps.account.models import Student
from apps.team.filters import TeamFilter, TeamTaskFilter
from apps.team.models import Team, TeamApply, TeamTask, TeamVacancies
from apps.team.serializers import TeamApplySerializer, TeamSerializer, TeamTaskSerializer, TeamTaskUpdateStatusSerializer, TeamVacanciesSerializer
from django.db.models import Q, Case, When, BooleanField
from django_filters.rest_framework import DjangoFilterBackend
from utils.exceptions import failure_response, failure_response_validation, success_response
from utils.permissions import IsLeaderOrMembers, IsStudent, IsTeamLeaderOrMember
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = (permissions.IsAuthenticated, IsStudent)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter] 
    filterset_class = TeamFilter
    search_fields = ['name', 'description']
    lookup_field = 'slug'

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Team.objects.all()
    
        student = Student.objects.filter(user=user).first()
        if not student:
            return Team.objects.none()
    
        return (Team.objects.filter(Q(leader=student) | Q(members=student))
                    .annotate(is_leader=Case(
                        When(leader=student, then=True),
                        default=False,
                        output_field=BooleanField())
                    )
                    .order_by('-is_leader')
                    .distinct()
                )
            

class TeamVacanciesViewSet(viewsets.ModelViewSet):
    queryset = TeamVacancies.objects.all()
    serializer_class = TeamVacanciesSerializer
    permission_classes = (permissions.IsAuthenticated, IsStudent)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['description', 'role']
    filterset_fields = ['team__slug']

        

class TeamApplyViewSet(viewsets.ModelViewSet):
    queryset = TeamApply.objects.all()
    serializer_class = TeamApplySerializer
    permission_classes = (permissions.IsAuthenticated, IsStudent)

    @action(detail=False, methods=['get'])
    def get_user(self, request):
        user = request.user
        student = Student.objects.filter(user=user).first()
        if not student:
            return success_response('TeamApply fetched successfully', [])
        return success_response('TeamApply fetched successfully', TeamApply.objects.filter(user=student))


 

class TeamTaskViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides `retrieve`, `create`, `list`, `update`, and `destroy` actions.
    """
    serializer_class = TeamTaskSerializer
    permission_classes = (permissions.IsAuthenticated, IsStudent)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['title', 'description']
    lookup_field = 'pk'
    filterset_class = TeamTaskFilter
    # queryset = TeamTask.objects.all()

    def get_queryset(self):
        """
        Optionally restricts the returned tasks to a given team,
        by filtering against a `team_id` query parameter in the URL.
        """

        team_slug = self.kwargs.get('team_slug')

        if team_slug:
            team = get_object_or_404(Team, slug=team_slug)
            return TeamTask.objects.filter(team=team)
        return TeamTask.objects.none()
    
    def get_serializer_context(self):
        """
        Pass 'team_slug' to serializer context.
        """
        context = super(TeamTaskViewSet, self).get_serializer_context()
        context['team_slug'] = self.kwargs.get('team_slug')
        return context
    

    
class UserTeamTaskList(generics.ListAPIView):
    serializer_class = TeamTaskSerializer
    ordering = ['due_time']
    permission_classes = (permissions.IsAuthenticated, IsStudent)
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return TeamTask.objects.all()
        student = Student.objects.filter(user=user).first()
        return TeamTask.objects.filter(Q(team__leader=student) | Q(team__members=student))