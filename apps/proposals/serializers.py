from rest_framework import serializers
from apps.proposals.models import Proposal, SubmissionsProposalApply
from apps.team.models import Team
from taggit.serializers import (TagListSerializerField,
                                TaggitSerializer)
from taggit.models import Tag
from django.db.models import Q

from utils.exceptions import failure_response_validation

class ProposalSerializer(TaggitSerializer,serializers.ModelSerializer):
    tag = TagListSerializerField()
    class Meta:
        model = Proposal
        fields = '__all__'
        read_only_fields = ['team']

    def create(self, validated_data):
        team_id = self.context['view'].kwargs.get('team_id')
        team = Team.objects.get(id=team_id)
        proposal = Proposal.objects.create(team=team, **validated_data)
        return proposal
    
    def validate(self, attrs):
        team_id = self.context['view'].kwargs.get('team_id')
        team = Team.objects.get(id=team_id)
        applied_submissions = team.submissions_proposals_apply.filter(Q(status='APPLIED') | Q(status='REJECTED'))
        if applied_submissions.exists():
            raise failure_response_validation("You can't create a proposal for a team that has an applied or rejected submission")

        return attrs

    
class TagSerializer(TaggitSerializer, serializers.ModelSerializer):
    
    class Meta:
        model = Tag
        fields = '__all__'

class SubmissionProposalApplySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionsProposalApply
        fields = '__all__'
        read_only_fields = ['lecturer']
    
    def create(self, validated_data):
        team_id = self.context['view'].kwargs.get('team_id')
        team = Team.objects.get(id=team_id)
        submission = SubmissionsProposalApply.objects.create(team=team, **validated_data)
        return submission

    def validate(self, attrs):
        team_id = self.context['view'].kwargs.get('team_id')
        team = Team.objects.get(id=team_id)
        applied_submissions = team.submissions_proposals_apply.filter(Q(status='APPLIED') | Q(status='REJECTED'))
        if applied_submissions.exists():
            raise failure_response_validation("You can't create a submission for a team that has an applied or rejected submission")
        return attrs