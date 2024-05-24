import django_filters
from .models import PKMActivitySchedule


class PKMActivityScheduleFilter(django_filters.FilterSet):
    date_year = django_filters.NumberFilter(method='filter_by_year')
    date_month = django_filters.NumberFilter(method='filter_by_month')

    class Meta:
        model = PKMActivitySchedule
        fields = ['date_year', 'date_month']

    def filter_by_year(self, queryset, name, value):
        return queryset.filter(start_date__year=value, end_date__year=value)

    def filter_by_month(self, queryset, name, value):
        return queryset.filter(start_date__month=value, end_date__month=value)