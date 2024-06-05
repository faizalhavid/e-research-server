from rest_framework import serializers

from apps.account.models import Lecturer, Student
from apps.team.models import Team, TeamApply, TeamTask, TeamVacancies
from utils.exceptions import failure_response_validation
from taggit.serializers import (TagListSerializerField,
                                TaggitSerializer)

class MemberSerializers(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ('id', 'full_name', 'phone_number', 'image')

class TeamSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(max_length=None, use_url=True, allow_null=True, required=False)
    members = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    lecturer = serializers.PrimaryKeyRelatedField(queryset=Lecturer.objects.all())
    user_role = serializers.SerializerMethodField()
    class Meta:
        model = Team
        fields = '__all__'
        read_only_fields = ('id', 'leader', 'created_at', 'updated_at','slug','user_role')

    
    def get_user_role(self, obj):
        user = self.context['request'].user
        
        if obj.leader.user_id == user.id:
            return 'leader'
        elif user.id in obj.members.values_list('user_id', flat=True):
            return 'member'
        else:
            return 'none'
        
    def validate(self, data):
        user = self.context['request'].user
        leader = Student.objects.get(user=user) if not user.is_superuser else None
        members = data.get('members')
        lecturer = data.get('lecturer')

        if Team.objects.filter(leader=leader, status='ACTIVE').exists():
            raise failure_response_validation({'leader': 'You only can be a leader in one active team'})
    
        if Team.objects.filter(lecturer=lecturer, status='ACTIVE').count >= 10:
            raise failure_response_validation('The lecturer has reached the maximum number of teams')

        if leader in members:
            raise failure_response_validation({'members': 'Leader cannot also be a member'})
    
        if any(Team.objects.filter(members=member).count() > 3 for member in members):
            raise failure_response_validation({'members': 'The member has joined the maximum number of teams'})
    
        unregistered_member = next((member for member in members if member.user is None), None)
        if unregistered_member:
            raise failure_response_validation({"members": f"{unregistered_member.full_name} is not registered in the system"})
        return data
    
    def to_representation(self, instance):
        response = super().to_representation(instance)

        response['leader'] = MemberSerializers(instance.leader).data
        response['members'] = MemberSerializers(instance.members.all(), many=True).data
        return response
    


class TeamVacanciesSerializer(TaggitSerializer,serializers.ModelSerializer):
    tags = TagListSerializerField()
    team = TeamSerializer(read_only=True)
    class Meta:
        model = TeamVacancies
        fields = '__all__'
    
   

    def validate(self, data):
        team = self.context['team']
        if team.status != 'ACTIVE':
            raise failure_response_validation('Team is not active')
        return data
    
class TeamApplySerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamApply
        fields = '__all__'
        read_only_fields = ('id', 'vacancies', 'user', 'created_at')
        extra_kwargs = {
            'resume': {'write_only': True},
        }
        
    def validate(self, data):
        vacancies = self.context['vacancies']
        user = self.    context['request'].user
        if vacancies.team.status != 'ACTIVE':
            raise failure_response_validation('Team is not active')
        if vacancies.team.members.filter(user=user).exists():
            raise failure_response_validation('You are already a member of this team')
        return data
    
    
class TeamTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamTask
        fields = '__all__'
        read_only_fields = ('id', 'team', 'created_at', 'updated_at')
        

    def create(self, validated_data):
        team_id = self.context['team_id']
        team = Team.objects.get(id=team_id)
        task = TeamTask.objects.create(team=team, **validated_data)
        return task
    
    
    def validate(self, data):
        print(self.context)
        team_id = self.context['team_id']
        team = Team.objects.get(id=team_id)
        
        if team.status != 'ACTIVE':
            raise failure_response_validation('Team is not active')
        return data