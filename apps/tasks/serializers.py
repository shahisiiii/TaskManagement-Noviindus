from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['assigned_to']

    def update(self, instance, validated_data):
        if validated_data.get('status') == 'Completed':
            if not validated_data.get('completion_report') or not validated_data.get('worked_hours'):
                raise serializers.ValidationError("Completion Report and Worked Hours are required when completing a task.")
        return super().update(instance, validated_data)

class TaskReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['completion_report', 'worked_hours']
