from django_filters import rest_framework as filters
import django_filters
from .models import PKMActivitySchedule, PKMIdeaContribute
from taggit.models import Tag
from django.db.models import Q

class PKMActivityScheduleFilter(django_filters.FilterSet):
    date_year = django_filters.NumberFilter(method='filter_by_year')
    date_month = django_filters.NumberFilter(method='filter_by_month')

    class Meta:
        model = PKMActivitySchedule
        fields = ['date_year', 'date_month']

    def filter_by_year(self, queryset, name, value):
        return queryset.filter(
            Q(start_date__year=value) | Q(end_date__year=value)
        )

    def filter_by_month(self, queryset, name, value):
        return queryset.filter(
            Q(start_date__month=value) | Q(end_date__month=value)
        )
    




class PKMIdeaContributeFilter(filters.FilterSet):
    tags = filters.CharFilter(method='filter_by_tags')
    team = filters.ChoiceFilter(choices=[('ALL', 'All'), ('APPLIED', 'Applied'), ('NOT_APPLIED', 'Not Applied')], method='filter_by_team')

    class Meta:
        model = PKMIdeaContribute
        fields = ['tags']

    def filter_by_tags(self, queryset, name, value):
        # Split tags by comma
        tags = value.split(',')
        return queryset.filter(tags__name__in=tags).distinct()
    
    def filter_by_team(self, queryset, name, value):
        if value == 'ALL':
            return queryset
        elif value == 'APPLIED':
            return queryset.filter(apply_teams__status='A')
        elif value == 'NOT_APPLIED':
            return queryset.exclude(apply_teams__status='A')
        return queryset
    
