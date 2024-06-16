
from django_filters import rest_framework as filters

from apps.content_hub.models import Article

class ArticleFilter(filters.FilterSet):
    tags = filters.CharFilter(method='filter_by_tags')

    class Meta:
        model = Article
        fields = ['tags']

    def filter_by_tags(self, queryset, name, value):
        # Split tags by comma
        tags = value.split(',')
        return queryset.filter(tags__name__in=tags).distinct()