from django.contrib import admin
from .api.models import Task, Comment

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1
    readonly_fields = ('author', 'created_at')
    fields = ('author', 'text', 'created_at')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'board', 'status', 'priority', 
        'assigned_to_display', 'reviewer_display', 'due_date', 'created_at'
    )
    list_filter = ('status', 'priority', 'board', 'due_date')
    search_fields = ('title', 'description', 'assigned_to__first_name', 'reviewer__first_name')
    ordering = ('-created_at',)
    inlines = [CommentInline]

    def assigned_to_display(self, obj):
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}".strip() or obj.assigned_to.email
        return "Unassigned"
    assigned_to_display.short_description = "Assignee"

    def reviewer_display(self, obj):
        if obj.reviewer:
            return f"{obj.reviewer.first_name} {obj.reviewer.last_name}".strip() or obj.reviewer.email
        return "No Reviewer"
    reviewer_display.short_description = "Reviewer"

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'task', 'author_display', 'short_text', 'created_at')
    search_fields = ('text', 'task__title', 'author__first_name', 'author__last_name')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

    def author_display(self, obj):
        if obj.author:
            return f"{obj.author.first_name} {obj.author.last_name}".strip() or obj.author.email
        return "Anonymous"
    author_display.short_description = "Author"

    def short_text(self, obj):
        return (obj.text[:60] + '...') if len(obj.text) > 60 else obj.text
    short_text.short_description = "Comment"