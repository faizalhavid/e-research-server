from apps.account.models import Guest, Lecturer, Student
from apps.account.serializers import GuestSerializer, LecturerSerializer, StudentSerializer, UserSerializer
from apps.pkm.models import PKMActivitySchedule, PKMIdeaContribute, PKMIdeaContributeApplyTeam, PKMProgram, PKMScheme
from rest_framework import serializers
from taggit.serializers import (TagListSerializerField,
                                TaggitSerializer)


from apps.team.models import Team
from apps.team.serializers import TeamSerializer
from utils.exceptions import failure_response, failure_response_validation


class PKMSchemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PKMScheme
        fields = ('id', 'name', 'abbreviation', 'description')

class PKMProgramSerializer(serializers.ModelSerializer):
    scheme = PKMSchemeSerializer(many=True)
    class Meta:
        model = PKMProgram
        fields = '__all__'

class PKMActivityScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PKMActivitySchedule
        fields = '__all__'


class PKMIdeaContributeSerializer(TaggitSerializer,serializers.ModelSerializer):
    tags = TagListSerializerField()
    team = serializers.SerializerMethodField()
    team_apply_status = serializers.SerializerMethodField()
    class Meta:
        model = PKMIdeaContribute
        fields = '__all__'
        read_only_fields = ('user', 'status', 'created', 'applied_date')

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)
    
    def validate(self, attrs):
        user = self.context['request'].user
        slug = attrs.get('slug')
        max_contributions = 5
        # Count the number of existing contributions by this user
        contributions_count = PKMIdeaContribute.objects.filter(user=user).count()

        if contributions_count >= max_contributions:
            raise failure_response_validation(f"User has reached the maximum number of contributions ({max_contributions})")
        
        # Check if slug is unique
        if PKMIdeaContribute.objects.filter(slug=slug).exists():
            raise failure_response_validation("Title has already been used for another idea contribute")

        return attrs
    
    def get_team(self, obj):
        try:
            idea_team_apply = obj.apply_teams.get(status='A')
            team = idea_team_apply.team
            return TeamSerializer(team, context=self.context).data
        except PKMIdeaContributeApplyTeam.DoesNotExist:
            return None
        
    def get_team_apply_status(self, obj):
        if not self.context['request'].user.groups.filter(name='Student').exists():
            return None
        student = Student.objects.get(user=self.context['request'].user)
        team = Team.objects.filter(leader=student, status='ACTIVE').first()
        idea_team_apply = obj.apply_teams.filter(status__in=['A', 'P', 'R'], team=team).first()
        return idea_team_apply.status if idea_team_apply else None
        
    def to_representation(self, instance):
        # Get default serialized data
        representation = super().to_representation(instance)
    
        # Get serialized User data
        user = UserSerializer(instance.user).data
        if instance.user.groups.filter(name='Student').exists():
            user['student'] = StudentSerializer(Student.objects.get(user=instance.user)).data
        elif instance.user.groups.filter(name='Lecturer').exists():
            user['lecturer'] = LecturerSerializer(Lecturer.objects.get(user=instance.user)).data
        elif instance.user.groups.filter(name='Guest').exists():
            user['guest'] = GuestSerializer(Guest.objects.get(user=instance.user)).data
    
        # Add User data to serialized data
        representation['user'] = user
    
        return representation



class PKMIdeaContributeApplyTeamSerializer(serializers.ModelSerializer):    

    class Meta:
        model = PKMIdeaContributeApplyTeam
        fields = '__all__'
        read_only_fields = ['slug', 'status', 'created', 'applied_date']

    def validate(self, attrs):
        idea_contribute = attrs.get('idea_contribute')
        team = attrs.get('team')
        submission = attrs.get('submission')  # Assuming submission is part of attrs
        title = attrs.get('title')  # Assuming title is part of attrs
    
        # Existing validations
        if team.status != 'ACTIVE':
            raise failure_response_validation('Team is not active')
    
        if idea_contribute.apply_teams.filter(team=team, status__in=['A', 'P']).exists():
            raise failure_response_validation("This team has already applied or been accepted for this idea contribute")
    
        if idea_contribute.apply_teams.filter(status='A').exists():
            raise failure_response_validation("You can't apply a team for an idea contribute that has an accepted team")
    
        if idea_contribute.user == team.leader.user:
            raise failure_response_validation("You can't apply your team for your own idea contribute")
    
        if PKMIdeaContributeApplyTeam.objects.filter(team=team, status='A').exclude(idea_contribute=idea_contribute).exists():
            raise failure_response_validation("This team has already applied to another idea")
    
        # New validation for unique_together constraint
        if self.instance:
            # If updating, exclude the current instance from the unique check
            if PKMIdeaContributeApplyTeam.objects.filter(team=team, submission=submission, title=title).exclude(pk=self.instance.pk).exists():
                raise failure_response_validation("You can't apply a team for the same submission and title")
        else:
            # For new instances, just check if any existing match the criteria
            if PKMIdeaContributeApplyTeam.objects.filter(team=team, submission=submission, title=title).exists():
                raise failure_response_validation("You can't apply a team for the same submission and title")
    
        return attrs

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        idea_contribute = PKMIdeaContributeSerializer(instance.idea_contribute, context=self.context).data
        representation['idea_contribute'] = idea_contribute
        return representation
