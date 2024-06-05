from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, filters, generics
from apps.account.models import Student
from apps.team.filters import TeamTaskFilter
from apps.team.models import Team, TeamApply, TeamTask, TeamVacancies
from apps.team.serializers import TeamApplySerializer, TeamSerializer, TeamTaskSerializer, TeamVacanciesSerializer
from django.db.models import Q, Case, When, BooleanField
from django_filters.rest_framework import DjangoFilterBackend
from utils.permissions import IsLeaderOrMembers, IsStudent
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = (permissions.IsAuthenticated, IsStudent)
    filter_backends = [filters.SearchFilter]
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
            
    def perform_create(self, serializer):
        if not self.request.user.is_superuser:
            serializer.save(leader=self.request.user)



class TeamVacanciesViewSet(viewsets.ModelViewSet):
    queryset = TeamVacancies.objects.all()
    serializer_class = TeamVacanciesSerializer
    permission_classes = (permissions.IsAuthenticated, IsStudent)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['description', 'role']
    filterset_fields = ['team__slug']
    lookup_field = 'slug'
        

class TeamApplyViewSet(viewsets.ModelViewSet):
    queryset = TeamApply.objects.all()
    serializer_class = TeamApplySerializer
    permission_classes = (permissions.IsAuthenticated, IsStudent)
    lookup_field = 'vacancies_id'

    @action(detail=False, methods=['get'])
    def get_user(self, request):
        user = request.user
        student = Student.objects.filter(user=user).first()
        if not student:
            return TeamApply.objects.none()
        return TeamApply.objects.filter(user=student)


 


class TeamTaskViewSet(viewsets.ModelViewSet):
    serializer_class = TeamTaskSerializer
    permission_classes = (permissions.IsAuthenticated, IsStudent)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['title', 'description']
    lookup_field = 'pk'
    filterset_class = TeamTaskFilter

    def get_queryset(self):
        user = self.request.user
        team = self.kwargs.get('team_id')
        if user.is_superuser:
            return TeamTask.objects.filter(team=team)

        student = Student.objects.filter(user=user).first()
        if not student:
            return TeamTask.objects.none()
        
        return TeamTask.objects.filter(team=team).filter(Q(team__leader=student) | Q(team__members=student))
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['team_id'] = self.kwargs.get('team_id')
        return context
    
class UserTeamTaskList(generics.ListAPIView):
    serializer_class = TeamTaskSerializer
    ordering = ['due_time']
    permission_classes = (permissions.IsAuthenticated, IsStudent)


    def get_queryset(self):
        user = self.request.user
        student = Student.objects.filter(user=user).first()
        return TeamTask.objects.filter(Q(team__leader=student) | Q(team__members=student))