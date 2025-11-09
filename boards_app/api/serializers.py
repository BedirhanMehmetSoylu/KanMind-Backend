from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Board
from task_app.api.models import Task

User = get_user_model()


class UserMiniSerializer(serializers.ModelSerializer):
    """Minimal user representation with ID, email, and full name."""
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

    def get_fullname(self, obj):
        """Combine first and last name into a single string."""
        return f"{obj.first_name} {obj.last_name}".strip()

class BoardListSerializer(serializers.ModelSerializer):
    """Board summary with counts of members and tasks."""
    title = serializers.CharField(source='name', read_only=True)
    owner_id = serializers.IntegerField(source='created_by.id', read_only=True)
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'member_count', 'ticket_count', 
                  'tasks_to_do_count', 'tasks_high_prio_count']

    def get_member_count(self, obj):
        """Return number of members on the board."""
        return obj.members.count()

    def get_ticket_count(self, obj):
        """Return total number of tasks on the board."""
        return Task.objects.filter(board=obj).count()

    def get_tasks_to_do_count(self, obj):
        """Return number of tasks with status 'to-do'."""
        return Task.objects.filter(board=obj, status='to-do').count()

    def get_tasks_high_prio_count(self, obj):
        """Return number of tasks with high priority."""
        return Task.objects.filter(board=obj, priority='high').count()
    
    
class BoardDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed Board view.
    Includes members and all related tasks.
    """
    title = serializers.CharField(source='name', read_only=True)
    owner_id = serializers.IntegerField(source='created_by.id', read_only=True)
    members = serializers.SerializerMethodField()
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']

    def get_members(self, obj):
        """Return list of members with id, email, fullname only."""
        return [
            {
                "id": m.id,
                "email": m.email,
                "fullname": f"{m.first_name} {m.last_name}".strip()
            }
            for m in obj.members.all()
        ]

    def get_tasks(self, obj):
        """Return list of tasks with minimal user info."""
        return [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "status": t.status,
                "priority": t.priority,
                "assignee": self._user_mini(t.assigned_to),
                "reviewer": self._user_mini(t.reviewer),
                "due_date": t.due_date,
                "comments_count": t.comments.count(),
            }
            for t in Task.objects.filter(board=obj)
        ]

    def _user_mini(self, user):
        """Helper to return minimal user info."""
        if not user:
            return None
        return {
            "id": user.id,
            "email": user.email,
            "fullname": f"{user.first_name} {user.last_name}".strip()
        }
    
    
class BoardUpdateSerializer(serializers.ModelSerializer):
    """Board update view with owner and member info."""
    title = serializers.CharField(source='name')
    owner_data = UserMiniSerializer(source='created_by', read_only=True)
    members_data = UserMiniSerializer(source='members', many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_data', 'members_data']