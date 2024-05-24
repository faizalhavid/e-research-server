from apps.pkm.models import PKMActivitySchedule, PKMScheme
from rest_framework import serializers

class PKMSchemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PKMScheme
        fields = ('id', 'name', 'abbreviation', 'description')



class PKMActivityScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PKMActivitySchedule
        fields = '__all__'
