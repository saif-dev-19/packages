from django.contrib import admin
from .models import Task
# Register your models here.

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "priority", "due_date", "created_at")
    list_filter = ("status", "priority", "due_date")
    search_fields = ("title",)
    ordering = ("-created_at",)