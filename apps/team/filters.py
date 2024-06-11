from django_filters import rest_framework as filters
from django.utils import timezone
from datetime import timedelta
from apps.account.models import Student
from apps.team.models import Team, TeamTask

class TeamTaskFilter(filters.FilterSet):
    due_in_days = filters.NumberFilter(method='filter_by_due_date')

    class Meta:
        model = TeamTask
        fields = ['title', 'description', 'due_time', 'completed', 'due_in_days']

class TeamTaskFilter(filters.FilterSet):
    due_in_days = filters.NumberFilter(method='filter_by_due_date')
    task_user = filters.CharFilter(method='filter_by_task_user')

    class Meta:
        model = TeamTask
        fields = ['title', 'description', 'due_time', 'completed', 'due_in_days']

    def filter_by_due_date(self, queryset, name, value):
        if value is not None:
            # Menghitung tanggal batas atas (3 hari dari sekarang)
            date_threshold = timezone.now() + timedelta(days=int(value))
            # Menghitung tanggal batas bawah (sekarang)
            date_now = timezone.now()
            # Filter dengan due_time antara sekarang dan 3 hari ke depan dan belum completed
            queryset = queryset.filter(
                due_time__gte=date_now,
                due_time__lte=date_threshold,
                completed=False
            ).order_by('created_at')[:5]
        return queryset

    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['due_time'].label = 'Due Time'
        self.filters['completed'].label = 'Completed'
        self.filters['title'].label = 'Title'
        self.filters['description'].label = 'Description'
        self.filters['due_in_days'].label = 'Due in Days'


class TeamFilter(filters.FilterSet):
    is_leader = filters.BooleanFilter(method='filter_is_leader')
    is_member = filters.BooleanFilter(method='filter_is_member')

    class Meta:
        model = Team
        fields = []

    def filter_is_leader(self, queryset, name, value):
        if value:
            user = self.request.user
            student = Student.objects.filter(user=user).first()
            return queryset.filter(leader=student)
        return queryset

    def filter_is_member(self, queryset, name, value):
        if value:
            user = self.request.user
            student = Student.objects.filter(user=user).first()
            return queryset.filter(members=student)
        return queryset