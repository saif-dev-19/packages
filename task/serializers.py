from rest_framework import serializers
from .models import Task, TaskStatus, TaskPriority


class TaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "status",
            "priority",
            "due_date",
            "completed_at",
            "created_at",
        ]


class TaskDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "due_date",
            "created_by_user_id",
            "created_by_email",
            "completed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_by_user_id",
            "created_by_email",
            "completed_at",
            "created_at",
            "updated_at",
        ]


class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "due_date",
        ]
        read_only_fields = ["id"]

    def validate_status(self, value):
        if value not in TaskStatus.values:
            raise serializers.ValidationError(
                f"Invalid status. Allowed values: {', '.join(TaskStatus.values)}"
            )
        if value == TaskStatus.COMPLETED and self.instance is None:
            raise serializers.ValidationError(
                "Cannot create a task with status 'completed'. Use the complete endpoint instead."
            )
        return value

    def validate_priority(self, value):
        if value not in TaskPriority.values:
            raise serializers.ValidationError(
                f"Invalid priority. Allowed values: {', '.join(TaskPriority.values)}"
            )
        return value

    def validate(self, attrs):
        due_date = attrs.get("due_date")
        if due_date is not None and self.instance is None and due_date <= self._now():
            raise serializers.ValidationError(
                {"due_date": "Due date must be in the future."}
            )

        return attrs
    
    @staticmethod
    def _now():
        from django.utils import timezone
        return timezone.now()