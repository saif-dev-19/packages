from django.db import models
from django.utils import timezone
from .choices import TaskStatus, TaskPriority



class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.PENDING,
    )
    priority = models.CharField(
        max_length=20,
        choices=TaskPriority.choices,
        default=TaskPriority.MEDIUM,
    )

    due_date = models.DateTimeField(null=True, blank=True)

    created_by_user_id = models.BigIntegerField(db_index=True)
    created_by_email = models.EmailField(blank=True)

    completed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_by_user_id", "status"]),
            models.Index(fields=["priority"]),
        ]

    def mark_completed(self):
        if self.status != TaskStatus.COMPLETED:
            self.status = TaskStatus.COMPLETED
            self.completed_at = timezone.now()
            self.save(update_fields=["status", "completed_at", "updated_at"])

    def __str__(self):
        return self.title