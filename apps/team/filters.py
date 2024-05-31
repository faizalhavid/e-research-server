
from django_filters import rest_framework as filters
from django.utils import timezone
from datetime import timedelta

from apps.team.models import TeamTask

class TeamTaskFilter(filters.FilterSet):
    due_in_days = filters.NumberFilter(method='filter_by_due_date')

    class Meta:
        model = TeamTask
        fields = ['title', 'description', 'due_time', 'completed', 'due_in_days']

    def filter_by_due_date(self, queryset, name, value):
        if value is not None:
            # Menghitung tanggal batas atas (3 hari dari sekarang)
            date_threshold = timezone.now() + timedelta(days=int(value))
            print(date_threshold)
            # Menghitung tanggal batas bawah (sekarang)
            date_now = timezone.now()
            # Filter dengan due_time antara sekarang dan 3 hari ke depan
            return queryset.filter(due_time__gte=date_now, due_time__lte=date_threshold)
        return queryset

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['due_time'].label = 'Due Time'
        self.filters['completed'].label = 'Completed'
        self.filters['title'].label = 'Title'
        self.filters['description'].label = 'Description'
        self.filters['due_in_days'].label = 'Due in Days'