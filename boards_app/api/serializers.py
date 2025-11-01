from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Board
from task_app.api.models import Task
from task_app.api.serializers import TaskSerializer

User = get_user_model()


class UserMiniSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'fullname']

    def get_fullname(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class BoardSerializer(serializers.ModelSerializer):
    created_by = UserMiniSerializer(read_only=True)
    members = UserMiniSerializer(many=True, read_only=True)
    title = serializers.CharField(source='name', read_only=True)
    member_count = serializers.SerializerMethodField()
    tasks = TaskSerializer(many=True, read_only=True)
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ['id', 'name', 'title', 'created_by', 'members', 'member_count', 'tasks', 'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count',]

    def get_member_count(self, obj):
        return obj.members.count()
    
    def get_ticket_count(self, obj):
        return Task.objects.filter(board=obj).count()

    def get_tasks_to_do_count(self, obj):
        return Task.objects.filter(board=obj, status='to-do').count()

    def get_tasks_high_prio_count(self, obj):
        return Task.objects.filter(board=obj, priority='high').count()