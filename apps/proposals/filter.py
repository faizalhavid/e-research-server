import django_filters
from taggit.models import Tag

from apps.proposals.models import SubmissionsProposalApply

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