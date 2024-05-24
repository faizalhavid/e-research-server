from rest_framework import viewsets, permissions, filters
from apps.account.models import Student
from apps.team.models import Team
from apps.team.serializers import TeamSerializer
from django.db.models import Q, Case, When, BooleanField


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    lookup_field = 'slug'

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:  
            return Team.objects.all()  
        else:
            try:
                student = Student.objects.get(user=user)  
                return (Team.objects.filter(Q(leader=student) | Q(members=student))
                  
                        .order_by('-is_leader')
                        .distinct())  # remove duplicates
            except Student.DoesNotExist:
                return Team.objects.none()  
            
    def perform_create(self, serializer):
        if not self.request.user.is_superuser:
            serializer.save(leader=self.request.user)