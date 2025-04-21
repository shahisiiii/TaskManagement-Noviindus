from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    assigned_to_details = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Task
        fields = '__all__'

    def update(self, instance, validated_data):
        if validated_data.get('status') == 'Completed':
            if not validated_data.get('completion_report') or not validated_data.get('worked_hours'):
                raise serializers.ValidationError("Completion Report and Worked Hours are required when completing a task.")
        return super().update(instance, validated_data)
    
    def get_assigned_to_details(self, obj):
        """
        Custom method to get the details of the assigned user.
        """
        user = obj.assigned_to
        return {
            'id': user.id,
            'username': user.username,  
            'email': user.email,  
            'user_role_name':user.user_role.role_name
        }


class TaskReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['completion_report', 'worked_hours']
