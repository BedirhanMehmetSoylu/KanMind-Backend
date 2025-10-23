from rest_framework import serializers
from .models import Task
from django.contrib.auth import get_user_model
from boards_app.api.models import Board
from .models import Comment

User = get_user_model()


class UserMiniSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'fullname']

    def get_fullname(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class TaskSerializer(serializers.ModelSerializer):
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

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'board',
            'assignee',
            'assignee_id',
            'reviewer',
            'reviewer_id',
            'status',
            'priority',
            'due_date',
            'created_at',
            'updated_at',
        ]

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'task', 'author', 'content', 'created_at']
        read_only_fields = ['task', 'author', 'created_at']

    def get_author(self, obj):
        if obj.author:
            return f"{obj.author.first_name} {obj.author.last_name}".strip() or obj.author.email
        return "Unbekannt"