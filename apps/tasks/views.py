from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Task
from .serializers import TaskSerializer, TaskReportSerializer
from apps.users.permissions import IsAdminOrSuperAdmin

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_queryset(self):
        if self.action == 'report' and self.request.user.user_role.role_code in ['Admin', 'SuperAdmin']:
            return Task.objects.filter(status='Completed')
        elif self.request.user.user_role.role_code in ['Admin', 'SuperAdmin']:
            return self.queryset
        print("test task user ")
        return Task.objects.filter(assigned_to=self.request.user)

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.assigned_to != request.user:
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=['get'], permission_classes=[IsAdminOrSuperAdmin])
    def report(self, request, pk=None):
        task = self.get_object()
        if task.status != "Completed":
            return Response({"detail": "Task is not completed."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = TaskReportSerializer(task)
        return Response(serializer.data)
