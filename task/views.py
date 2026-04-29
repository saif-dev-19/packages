from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Task, TaskStatus
from rest_framework.validators import ValidationError
from utils.response import common_response
from .models import Task
from .serializers import (
    TaskCreateUpdateSerializer,
    TaskDetailSerializer,
    TaskListSerializer,
)
from .services import complete_task


class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    filterset_fields = ["status", "priority"]
    search_fields = ["title"]
    ordering_fields = ["created_at", "updated_at", "due_date", "completed_at", "priority"]
    ordering = ["-created_at"]

    def get_queryset(self):
        if self.action == "update" or self.action == "partial_update" or self.action == "complete":
            return Task.objects.filter(
                created_by_user_id=self.request.user.id
            ).order_by("-created_at")
        
        if self.request.user.is_staff or self.request.user.is_superuser:
            return Task.objects.all().order_by("-created_at")
         
        return Task.objects.filter(
            created_by_user_id=self.request.user.id
        ).order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "list":
            return TaskListSerializer
        if self.action == "retrieve":
            return TaskDetailSerializer
        return TaskCreateUpdateSerializer

    def perform_create(self, serializer):
        serializer.save(
            created_by_user_id=self.request.user.id,
            created_by_email=self.request.user.email,
        )
    
    
    def perform_update(self, serializer):
        status_before = self.get_object().status
        if status_before == TaskStatus.COMPLETED and serializer.validated_data.get("status") != TaskStatus.COMPLETED:
            raise ValidationError("Cannot change status of a completed task.")
        serializer.save()


    @action(detail=True, methods=["post"], url_path="complete")
    def complete(self, request, pk=None):
        task = self.get_object()
        task = complete_task(task=task)

        return common_response(
            success=True,
            message="Task marked as completed",
            data=TaskDetailSerializer(task).data,
            status_code=status.HTTP_200_OK
        )