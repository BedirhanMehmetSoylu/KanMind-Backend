from datetime import timedelta

from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import generics, status, permissions

from .models import Task, Comment
from .serializers import TaskSerializer, CommentSerializer, TaskUpdateSerializer
from boards_app.api.models import Board

class AssignedTasksView(APIView):
    """Handles retrieval of all tasks assigned to the authenticated user."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return tasks assigned to the user with recent stats."""
        user = request.user
        tasks = Task.objects.filter(assigned_to=user)
        serializer = TaskSerializer(tasks, many=True)
        
        response = Response(serializer.data, status=status.HTTP_200_OK)
        response['X-Tasks-Done-Recently'] = self.get_tasks_done_recently(tasks)
        return response

    def get_tasks_done_recently(self, tasks):
        """Return count of tasks done in the last 14 days."""
        two_weeks_ago = timezone.now() - timedelta(days=14)
        return tasks.filter(status='done', updated_at__gte=two_weeks_ago).count()


class ReviewingTasksView(APIView):
    """Handles retrieval of all tasks where the user is assigned as reviewer."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return tasks where user is reviewer with recent stats."""
        user = request.user
        tasks = Task.objects.filter(reviewer=user)
        serializer = TaskSerializer(tasks, many=True)
        
        response = Response(serializer.data, status=status.HTTP_200_OK)
        response['X-Tasks-Done-Recently'] = self.get_tasks_done_recently(tasks)
        return response

    def get_tasks_done_recently(self, tasks):
        """Return count of tasks done in the last 14 days."""
        two_weeks_ago = timezone.now() - timedelta(days=14)
        return tasks.filter(status='done', updated_at__gte=two_weeks_ago).count()
    
    
class BoardTaskListView(APIView):
    """Lists all tasks for a specific board."""
    permission_classes = [IsAuthenticated]

    def get(self, request, board_id):
        """
        Return all tasks for the board with the given ID.

        If the board does not exist, returns 404.
        """
        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            return Response({"detail": "Board not found"}, status=status.HTTP_404_NOT_FOUND)

        tasks = Task.objects.filter(board=board).select_related('assigned_to', 'reviewer')
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
    
    
class TaskCreateView(APIView):
    """Handles creation of new tasks."""
    
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Validate data, check board membership, and create a task. Returns 201, 400, 403, or 404."""
        data = request.data.copy()
        try:
            board = Board.objects.get(id=data.get("board"))
        except Board.DoesNotExist:
            return Response({"detail": "Board not found. The Board with this id doesnt exist."}, status=404)
        if request.user != board.created_by and request.user not in board.members.all():
            return Response({"detail": "Not allowed. The User needs to be Member of the Board to create a Task."}, status=403)
        serializer = TaskSerializer(data=data)
        if serializer.is_valid():
            return Response(TaskSerializer(serializer.save()).data, status=201)
        return Response(serializer.errors, status=400)
    
    
class TaskDetailView(APIView):
    """Retrieve, update, or delete a specific task."""

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """Return details of a specific task by its ID."""
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response({"detail": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        """Update a task; only board members allowed. Board & comments_count not shown."""
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response({"detail": "Task not found. This Task-ID doesnt exist."}, status=404)
        
        board = task.board
        if request.user != board.created_by and request.user not in board.members.all():
            return Response({"detail": "Not allowed. Must be a board member."}, status=403)

        serializer = TaskUpdateSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        """Delete a specific task by its ID."""
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response({"detail": "Task not found. This Task-ID doesnt exist."}, status=status.HTTP_404_NOT_FOUND)

        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class CommentListCreateView(APIView):
    """List or create comments for a specific task with proper status codes."""
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        """Return all comments for a task. 403 if not board member, 404 if task missing."""
        try:
            task = Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            return Response({"detail": "Task not found. This Task-ID doesnt exist."}, status=404)

        if request.user != task.board.created_by and request.user not in task.board.members.all():
            return Response({"detail": "Not allowed. Must be a board member."}, status=403)

        comments = task.comments.order_by('created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=200)

    def post(self, request, task_id):
        """Create a comment for a task. 201 on success, 400 on invalid data, 403/404 as above."""
        try:
            task = Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            return Response({"detail": "Task not found. This Task-ID doesnt exist."}, status=404)

        if request.user != task.board.created_by and request.user not in task.board.members.all():
            return Response({"detail": "Not allowed. Must be a board member."}, status=403)

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(task=task, author=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    

class CommentDeleteView(APIView):
    """Delete a comment if the logged-in user is the author."""

    permission_classes = [IsAuthenticated]

    def delete(self, request, task_id, pk):
        """Delete a specific comment by ID if the user is the author."""
        try:
            comment = Comment.objects.get(pk=pk, task_id=task_id)
        except Comment.DoesNotExist:
            return Response({"detail": "Comment or Task not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if comment.author != request.user:
            return Response({"detail": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)
        
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class DashboardView(APIView):
    """Provides dashboard statistics for the logged-in user."""

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Returns all dashboard-related statistics for the logged-in user."""
        user = request.user

        data = {
            "tasks_done_recently": self.get_tasks_done_recently(),
            "tickets_distribution": self.get_tickets_distribution(),
            "urgent_to_do": self.get_urgent_tasks(),
            "your_tasks": self.get_recent_user_tasks(user),
            "tasks_insights": self.get_task_insights(user),
        }
        return Response(data, status=status.HTTP_200_OK)

    def get_tasks_done_recently(self):
        """Count tasks marked as done within the last 14 days."""
        two_weeks_ago = timezone.now() - timedelta(days=14)
        return Task.objects.filter(status='done', updated_at__gte=two_weeks_ago).count()

    def get_tickets_distribution(self):
        """Return the count of tasks per status."""
        return {
            'to_do': Task.objects.filter(status='to-do').count(),
            'in_progress': Task.objects.filter(status='in-progress').count(),
            'review': Task.objects.filter(status='review').count(),
            'done': Task.objects.filter(status='done').count(),
        }

    def get_urgent_tasks(self):
        """Return count and next deadline for urgent 'to-do' tasks."""
        urgent_tasks = Task.objects.filter(status='to-do', due_date__isnull=False).order_by('due_date')
        next_deadline = None
        if urgent_tasks.exists():
            next_task = urgent_tasks.first()
            next_deadline = {
                "id": next_task.id,
                "title": next_task.title,
                "due_date": next_task.due_date
            }
        return {
            "count": urgent_tasks.count(),
            "next_deadline": next_deadline
        }

    def get_recent_user_tasks(self, user):
        """Return the 5 most recently updated tasks assigned to the user."""
        tasks = Task.objects.filter(assigned_to=user).order_by('-updated_at')[:5]
        return TaskSerializer(tasks, many=True).data

    def get_task_insights(self, user):
        """Return counts of user's assigned and review tasks."""
        return {
            "assigned_to_you": Task.objects.filter(assigned_to=user).count(),
            "to_review": Task.objects.filter(reviewer=user).count(),
        }