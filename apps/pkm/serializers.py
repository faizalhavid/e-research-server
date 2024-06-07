from apps.account.models import Guest, Lecturer, Student
from apps.account.serializers import UserSerializer
from apps.pkm.models import PKMActivitySchedule, PKMIdeaContribute, PKMIdeaContributeApplyTeam, PKMProgram, PKMScheme
from rest_framework import serializers
from taggit.serializers import (TagListSerializerField,
                                TaggitSerializer)

from apps.team.serializers import TeamSerializer


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
    class Meta:
        model = PKMIdeaContribute
        fields = '__all__'
        read_only_fields = ('user', 'status', 'created', 'applied_date')

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)
    
    def get_team(self, obj):
        try:
            idea_team_apply = obj.apply_teams.get(status='A')
            team = idea_team_apply.team
            return TeamSerializer(team, context=self.context).data
        except PKMIdeaContributeApplyTeam.DoesNotExist:
            return None
        
    def to_representation(self, instance):
        # Get default serialized data
        representation = super().to_representation(instance)
    
        # Get serialized User data
        user = UserSerializer(instance.user).data
        if instance.user.groups.filter(name='Student').exists():
            user['student'] = Student.objects.get(user=instance.user).id
        elif instance.user.groups.filter(name='Lecturer').exists():
            user['lecturer'] = Lecturer.objects.get(user=instance.user).id
        elif instance.user.groups.filter(name='Guest').exists():
            user['guest'] = Guest.objects.get(user=instance.user).id
    
        # Add User data to serialized data
        representation['user'] = user
    
        return representation



class PKMIdeaContributeApplyTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = PKMIdeaContributeApplyTeam
        fields = '__all__'
