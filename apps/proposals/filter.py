from django.shortcuts import get_object_or_404
import django_filters
from taggit.models import Tag

from apps.proposals.models import SubmissionsProposalApply
from django.db.models import Count, Max
from django.contrib.contenttypes.models import ContentType


# class ProposalFilter(django_filters.FilterSet):
#     team = django_filters.CharFilter(field_name='team__name')
#     tag = django_filters.ModelMultipleChoiceFilter(field_name='tag__name', to_field_name='name', queryset=Tag.objects.all())
#     lecturer = django_filters.CharFilter(field_name='team__lecturer__name')

#     class Meta:
#         model = Proposal
#         fields = ['team', 'tag', 'lecturer']

class SubmissionProposalApplyFilter(django_filters.FilterSet):
    lecturer = django_filters.CharFilter(field_name='lecturer__name')
    status = django_filters.CharFilter(field_name='status')
    tag = django_filters.ModelMultipleChoiceFilter(field_name='tag__name', to_field_name='name', queryset=Tag.objects.all())

    class Meta:
        model = SubmissionsProposalApply
        fields = ['lecturer', 'status','team','tag', 'category']


class TagFilter(django_filters.FilterSet):
    popular = django_filters.BooleanFilter(method='filter_popular')

    class Meta:
        model = Tag
        fields = []

    def filter_popular(self, queryset, name, value):
        if value:
    
            model_name = self.request.GET.get('leads')
            print(model_name)
            if model_name:
                content_type = get_object_or_404(ContentType, model=model_name.lower())
                print(content_type)
                # Filter TaggedItem instances by this content type
                queryset = queryset.filter(taggit_taggeditem_items__content_type=content_type)
            
            max_usage = queryset.annotate(usage_count=Count('taggit_taggeditem_items')).aggregate(max_usage=Max('usage_count'))['max_usage']
            
            if max_usage is not None:
               if max_usage ==1 :
                    return queryset[:5]
               else:
                    # Define a dynamic popularity threshold, e.g., 50% of the maximum usage
                    popularity_threshold = max_usage * 0.5
                    
                    # Annotate each tag with its usage count for the specific model
                    queryset = queryset.annotate(usage_count=Count('taggit_taggeditem_items'))
                    
                    # Filter tags by the dynamic popularity threshold
                    queryset = queryset.filter(usage_count__gt=popularity_threshold)
        return queryset