from rest_framework import serializers

from apps.account.models import Lecturer, Student
from apps.team.models import Team
from utils.exceptions import failure_response_validation


class MemberSerializers(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ('id', 'full_name', 'phone_number', 'image')

class TeamSerializer(serializers.ModelSerializer):
    leader = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    image = serializers.ImageField(max_length=None, use_url=True, allow_null=True, required=False)
    lecturer = serializers.PrimaryKeyRelatedField(queryset=Lecturer.objects.all(), allow_null=True, required=False)
    members = serializers.PrimaryKeyRelatedField(many=True, queryset=Student.objects.all())

    class Meta:
        model = Team
        fields = '__all__'
        read_only_fields = ('id', 'leader', 'created_at', 'updated_at')
        extra_kwargs = {
         'description': {'write_only': True},
        }
        
    def validate(self, data):
        leader = data.get('leader')
        members = data.get('members')
        print(data)
        print(members)

        if Team.objects.filter(leader=leader, status='ACTIVE').exists():
            raise failure_response_validation({'leader': 'You only can be a leader in one active team'})
    
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
