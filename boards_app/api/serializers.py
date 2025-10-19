from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Board
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

    class Meta:
        model = Board
        fields = ['id', 'name', 'title', 'created_by', 'members', 'member_count', 'tasks']

    def get_member_count(self, obj):
        return obj.members.count()