from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Task, Comment

User = get_user_model()


class UserMiniSerializer(serializers.ModelSerializer):
    """
    Minimal user serializer for nested representation in tasks/comments.
    Includes id, email, first_name, last_name, and full name.
    """
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

    def get_fullname(self, obj):
        """Return the user's full name, or just first_name if last_name is missing."""
        return f"{obj.first_name} {obj.last_name}".strip()


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for Task model including nested user info, assignment,
    review, and computed comment count.
    """
    assignee = UserMiniSerializer(source='assigned_to', read_only=True)
    reviewer = UserMiniSerializer(read_only=True)

    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assigned_to',
        write_only=True,
        required=False,
        allow_null=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='reviewer',
        write_only=True,
        required=False,
        allow_null=True
    )

    comments_count = serializers.SerializerMethodField()
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Task
        fields = [
            'id',
            'board',
            'title',
            'description',
            'status',
            'priority',
            'assignee',
            'assignee_id',
            'reviewer',
            'reviewer_id',
            'due_date',
            'comments_count',
            'created_by'
        ]

    def get_comments_count(self, obj):
        """Return number of comments on this task."""
        return getattr(obj, 'comments', []).count() if hasattr(obj, 'comments') else 0
    
class TaskUpdateSerializer(serializers.ModelSerializer):
    """Serializer für PATCH-Updates, ohne board und comments_count."""
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assigned_to',
        write_only=True,
        required=False,
        allow_null=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='reviewer',
        write_only=True,
        required=False,
        allow_null=True
    )
    assignee = UserMiniSerializer(source='assigned_to', read_only=True)
    reviewer = UserMiniSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority', 
                  'assignee', 'reviewer', 'assignee_id', 'reviewer_id', 'due_date']

class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model.
    Returns the author as a full name or email if full name is missing.
    """
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'author', 'content']
        read_only_fields = ['task', 'author', 'created_at']

    def get_author(self, obj):
        """Return the comment author's full name, or email if full name missing."""
        if obj.author:
            return f"{obj.author.first_name} {obj.author.last_name}".strip() or obj.author.email
        return "Unbekannt"