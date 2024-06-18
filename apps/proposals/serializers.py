from django.shortcuts import get_object_or_404
from rest_framework import serializers
from apps.account.models import Student
from apps.pkm.serializers import PKMProgramSerializer
from apps.proposals.models import  SubmissionProposal, SubmissionsProposalApply
from apps.team.models import Team
from taggit.serializers import (TagListSerializerField,
                                TaggitSerializer)
from taggit.models import Tag
from django.db.models import Q

from apps.team.serializers import TeamSerializer
from utils.exceptions import failure_response_validation

# class ProposalSerializer(TaggitSerializer,serializers.ModelSerializer):
#     tag = TagListSerializerField()
#     class Meta:
#         model = Proposal
#         fields = '__all__'
#         read_only_fields = ['team']

#     def create(self, validated_data):
#         team_id = self.context['view'].kwargs.get('team_id')
#         team = Team.objects.get(id=team_id)
#         proposal = Proposal.objects.create(team=team, **validated_data)
#         return proposal
    
#     def validate(self, attrs):
#         team_id = self.context['view'].kwargs.get('team_id')
#         team = Team.objects.get(id=team_id)
#         applied_submissions = team.submissions_proposals_apply.filter(Q(status='APPLIED') | Q(status='REJECTED'))
#         if applied_submissions.exists():
#             raise failure_response_validation("You can't create a proposal for a team that has an applied or rejected submission")

#         return attrs

    
class SubmissionProposalSerializer(serializers.ModelSerializer):
    count_of_applicants = serializers.SerializerMethodField()
    program = PKMProgramSerializer()
    team_apply_status = serializers.SerializerMethodField()
    class Meta:
        model = SubmissionProposal
        fields = '__all__'

    def get_count_of_applicants(self, obj):
        return obj.applies.count()
    
    def get_team_apply_status(self, obj):
        if not self.context['request'].user.groups.filter(name='Student').exists():
            return None

        student = get_object_or_404(Student, user=self.context['request'].user)
        team = Team.objects.filter(Q(members=student) | Q(leader=student)).first()
        if team : 
            proposal_apply = obj.applies.filter(status__in=['APPLIED', 'REJECTED','REVISION','PASSED', 'PASSED FUNDING'], team=team).first()
            return proposal_apply.status if proposal_apply else None
        return None


class TagSerializer(TaggitSerializer, serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class SubmissionProposalApplySerializer(serializers.ModelSerializer, TaggitSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = SubmissionsProposalApply
        fields = '__all__'
        read_only_fields = ['lecturer','slug']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        team_serializer_context = self.context
        data['team'] = TeamSerializer(instance.team, context=team_serializer_context).data
        data['submission'] = SubmissionProposalSerializer(instance.submission, context=team_serializer_context).data
        return data


    

    def validate(self, attrs):
        submission = attrs.get('submission')
        status = attrs.get('status')
        team = attrs.get('team')

        if submission.title == 'REVISION' and status == 'REVISION':
            # If both conditions are met, validation passes for REVISION cases
            return attrs

        # Fetch the period of the current submission
        current_period = submission.program.period

        # Check for existing applications by the same team for any submission within the same period
        existing_applications = SubmissionsProposalApply.objects.filter(
            team=team,
            submission__program__period=current_period
        )

        if self.instance:
            # Exclude the current instance to allow updates
            existing_applications = existing_applications.exclude(id=self.instance.id)

        if existing_applications.exists():
            # If an existing application is found, raise a ValidationError
            raise serializers.ValidationError(f'The team {team.name} has already applied for a submission in the period {current_period}.')

        return attrs