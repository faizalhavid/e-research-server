from rest_framework import viewsets, permissions, filters, generics
from apps.account.models import Student
from apps.team.models import Team, TeamApply, TeamTask, TeamVacancies
from apps.team.serializers import TeamApplySerializer, TeamSerializer, TeamTaskSerializer, TeamVacanciesSerializer
from django.db.models import Q, Case, When, BooleanField

from utils.permissions import IsLeaderOrMembers, IsStudent


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = (permissions.IsAuthenticated, IsStudent)
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    

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
    # permission_classes = (permissions.IsAuthenticated, IsLeaderOrMembers)
    permission_classes = (permissions.IsAuthenticated, )
    filter_backends = [filters.SearchFilter]
    search_fields = ['description', 'role']
    lookup_field = 'team_id'

    def get_queryset(self):
        user = self.request.user
        team = self.kwargs.get('team_id')
        if user.is_superuser:
            return TeamVacancies.objects.all()

        student = Student.objects.filter(user=user).first()
        if not student:
            return TeamVacancies.objects.none()
        
        return TeamVacancies.objects.filter(team=team).filter(Q(team__leader=student) | Q(team__members=student))

class TeamApplyViewSet(viewsets.ModelViewSet):
    queryset = TeamApply.objects.all()
    serializer_class = TeamApplySerializer
    permission_classes = (permissions.IsAuthenticated, IsStudent)
    lookup_field = 'vacancies_id'

 


class TeamTaskViewSet(viewsets.ModelViewSet):
    queryset = TeamTask.objects.all()
    serializer_class = TeamTaskSerializer
    permission_classes = (permissions.IsAuthenticated, IsLeaderOrMembers)
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']
    lookup_field = 'team_id'

    def get_queryset(self):
        user = self.request.user
        team = self.kwargs.get('team_id')
        if user.is_superuser:
            return TeamTask.objects.all()

        student = Student.objects.filter(user=user).first()
        if not student:
            return TeamTask.objects.none()
        
        return TeamTask.objects.filter(team=team).filter(Q(team__leader=student) | Q(team__members=student))
    

    
class UserTeamTaskList(generics.ListAPIView):
    serializer_class = TeamTaskSerializer
    ordering = ['due_time']
    permission_classes = (permissions.IsAuthenticated, IsStudent)


    def get_queryset(self):
        user = self.request.user
        student = Student.objects.filter(user=user).first()

        return TeamTask.objects.filter(Q(team__leader=student) | Q(team__members=student))