from django.shortcuts import get_object_or_404
from rest_framework import serializers

from apps.account.models import Lecturer, Student
from apps.account.serializers import LecturerSerializer
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
        print(obj.leader.user_id, user.id,obj.name)
        if obj.leader.user_id == user.id:
            return 'leader'
        elif user.id in obj.members.values_list('user_id', flat=True):
            return 'member'
        else:
            return 'none'
        
    def create(self, validated_data):
        user = self.context['request'].user
        leader = Student.objects.get(user=user) if not user.is_superuser else None
        members = validated_data.pop('members')
        team = Team.objects.create(leader=leader, **validated_data)
        team.members.set(members)
        return team
        
    def validate(self, data):
        user = self.context['request'].user
        leader = Student.objects.get(user=user) if not user.is_superuser else None
        members = data.get('members')
        lecturer = data.get('lecturer')

        if Team.objects.filter(leader=leader, status='ACTIVE').exists():
            raise failure_response_validation({'leader': 'You only can be a leader in one active team'})
    
        if Team.objects.filter(lecturer=lecturer, status='ACTIVE').count() >= 10:
            raise failure_response_validation('The lecturer has reached the maximum number of teams')

        if any(member.user == user for member in members):
            raise failure_response_validation({'members': 'Leader cannot also be a member'})
    
        if any(Team.objects.filter(members=member).count() > 3 for member in members):
            raise failure_response_validation({'members': 'The member has joined the maximum number of teams'})
        
        
    
        unregistered_member = next((member for member in members if hasattr(member, 'user') and member.user is None), None)
        if unregistered_member:
            raise failure_response_validation({"members": f"{unregistered_member.full_name} is not registered in the system"})
        return data
    
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['lecturer'] = LecturerSerializer(instance.lecturer).data
        response['leader'] = MemberSerializers(instance.leader).data
        response['members'] = MemberSerializers(instance.members.all(), many=True).data
        return response
    


class TeamVacanciesSerializer(TaggitSerializer,serializers.ModelSerializer):
    tags = TagListSerializerField()
    team = TeamSerializer(read_only=True)
    user_apply_status = serializers.SerializerMethodField()

    class Meta:
        model = TeamVacancies
        fields = '__all__'
    
   
    def get_user_apply_status(self, obj):
        user = self.context['request'].user
        try:
            student = Student.objects.get(user=user)
            team_apply = TeamApply.objects.filter(user=student, vacanicies=obj).first()
            if team_apply:
                return team_apply.status  # Mengembalikan nilai dari field status
        except Student.DoesNotExist:
            return None
        return None
    
    def validate(self, data):
        team = self.instance.team if self.instance else data.get('team')
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

    def create(self, validated_data):
        user = self.context['request'].user
        student = get_object_or_404(Student, user=user)
        apply = TeamApply.objects.create(user=student,  **validated_data)
        return apply
        
    def validate(self, data):
        vacancies = self.instance.vacanicies if self.instance else data.get('vacanicies')
        user = self.context['request'].user
        # Ensure you're getting a Student instance here
        student = get_object_or_404(Student, user=user)
        # Use the student instance for filtering, not the user directly
        if TeamApply.objects.filter(user=student, vacanicies=vacancies).exists():
            raise failure_response_validation('You already applied to this vacancies')
        if Team.objects.filter(members=student, status='ACTIVE').exists():
            raise failure_response_validation('You already joined a team')
        if Team.objects.filter(leader=student, status='ACTIVE').exists():
            raise failure_response_validation('You already lead a team')
        if vacancies.team.  status != 'ACTIVE':
            raise failure_response_validation('Team is not active')
        
        return data
        
    
    
class TeamTaskSerializer(serializers.ModelSerializer):
    team_name = serializers.SerializerMethodField()
    class Meta:
        model = TeamTask
        fields = '__all__'
        read_only_fields = ('id', 'team', 'created_at', 'updated_at')
        

    def create(self, validated_data):
        team_slug = self.context['team_slug']
        team = Team.objects.get(slug=team_slug)
        task = TeamTask.objects.create(team=team, **validated_data)
        return task
    
    def get_team_name(self, obj):
        team_slug = self.context.get('team_slug')  # Use .get() to avoid KeyError
        if team_slug:
            team = Team.objects.get(slug=team_slug)
            return team.name
        return None  # Return None or a default value if 'team_slug' is not in context
    
    def validate(self, data):
        team_slug = self.context['team_slug']
        team = Team.objects.get(slug=team_slug)
        
        if team.status != 'ACTIVE':
            raise failure_response_validation('Team is not active')
        return data

class TeamTaskUpdateStatusSerializer (serializers.ModelSerializer):
    class Meta:
        model = TeamTask
        fields = ('completed',)
        read_only_fields = ('id', 'team', 'title', 'description', 'created_at', 'updated_at')
        
    def validate(self, data):
        if self.instance.status == 'DONE':
            raise failure_response_validation('Task is already done')
        return data