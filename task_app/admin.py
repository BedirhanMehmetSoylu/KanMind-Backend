from django.contrib import admin
from .api.models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'board', 'assignee_display', 'reviewer_display', 
        'status', 'priority', 'due_date', 'created_at', 'updated_at'
    )
    list_filter = ('status', 'priority', 'board')
    search_fields = ('title', 'description', 'assigned_to__first_name', 'assigned_to__last_name', 'reviewer__first_name', 'reviewer__last_name')
    ordering = ('-created_at',)

    def assignee_display(self, obj):
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}".strip()
        return "Unassigned"
    assignee_display.short_description = 'Assignee'

    def reviewer_display(self, obj):
        if obj.reviewer:
            return f"{obj.reviewer.first_name} {obj.reviewer.last_name}".strip()
        return "Unassigned"
    reviewer_display.short_description = 'Reviewer'
