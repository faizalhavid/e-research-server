from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType

from apps.pkm.serializers import PKMActivityScheduleSerializer, PKMIdeaContributeApplyTeamSerializer, PKMIdeaContributeSerializer, PKMProgramSerializer
from apps.proposals.serializers import SubmissionProposalApplySerializer
from apps.team.serializers import TeamApplySerializer, TeamSerializer, TeamTaskSerializer
from .models import Notification




class NotificationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['uid', 'user', 'message', 'read', 'timestamp', 'type']


class NotificationDetailSerializer(serializers.ModelSerializer):
    related_object = serializers.SerializerMethodField()
    class Meta:
        model = Notification
        fields = '__all__'

    def get_related_object(self, obj):
        serializer_mapping = {
            'pkmideacontribute': PKMIdeaContributeSerializer,
            'pkmactivityschedule': PKMActivityScheduleSerializer,
            'pkmprogram': PKMProgramSerializer,
            'pkmideacontributeapplyteam': PKMIdeaContributeApplyTeamSerializer,
            'team': TeamSerializer,
            'teamapply': TeamApplySerializer,
            'teamtask': TeamTaskSerializer,
            'submissionsproposalapply': SubmissionProposalApplySerializer,
        }
    
        content_type = obj.content_type
        if content_type is None:
            return None
    
        object_id = obj.object_id
        model_class = content_type.model_class()
        if model_class is None:
            return None
    
        model_name = model_class._meta.model_name.lower()
    
        try:
            instance = model_class.objects.get(id=object_id)
            serializer_class = serializer_mapping.get(model_name)
    
            if serializer_class:
                # Pass the context to the serializer
                serializer = serializer_class(instance, context=self.context)
                serialized_data = serializer.data
                # Add a 'type' field to indicate the type of component to be used
                serialized_data['type'] = model_name
                return serialized_data
            else:
                # If no serializer is found, return a basic structure with 'type'
                return {'id': object_id, 'type': model_name}
        except model_class.DoesNotExist:
            return None