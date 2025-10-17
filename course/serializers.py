from rest_framework import serializers
from .models import Program

class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = ['id', 'title', 'summary', 'absolute_url']
        read_only_fields = ['id', 'absolute_url']
    
    absolute_url = serializers.SerializerMethodField()
    
    def get_absolute_url(self, obj):
        return obj.get_absolute_url()