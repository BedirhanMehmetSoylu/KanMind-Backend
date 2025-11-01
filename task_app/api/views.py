from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import generics, status, viewsets, permissions
from datetime import timedelta
from django.utils import timezone

from .models import Task, Comment
from .serializers import TaskSerializer, CommentSerializer
from boards_app.api.models import Board

class AssignedTasksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        tasks = Task.objects.filter(assigned_to=user)
        serializer = TaskSerializer(tasks, many=True)

        now = timezone.now()
        two_weeks_ago = now - timedelta(days=14)

        tasks_done_recently = tasks.filter(
            status='done', updated_at__gte=two_weeks_ago
        ).count()

        tickets_distribution = {
            'to_do': tasks.filter(status='to-do').count(),
            'in_progress': tasks.filter(status='in-progress').count(),
            'review': tasks.filter(status='review').count(),
            'done': tasks.filter(status='done').count(),
        }

        response = Response(serializer.data, status=status.HTTP_200_OK)
        response['X-Tasks-Done-Recently'] = tasks_done_recently
        return response


class ReviewingTasksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        tasks = Task.objects.filter(reviewer=user)
        serializer = TaskSerializer(tasks, many=True)

        now = timezone.now()
        two_weeks_ago = now - timedelta(days=14)

        tasks_done_recently = tasks.filter(
            status='done', updated_at__gte=two_weeks_ago
        ).count()

        tickets_distribution = {
            'to_do': tasks.filter(status='to-do').count(),
            'in_progress': tasks.filter(status='in-progress').count(),
            'review': tasks.filter(status='review').count(),
            'done': tasks.filter(status='done').count(),
        }

        response = Response(serializer.data, status=status.HTTP_200_OK)
        response['X-Tasks-Done-Recently'] = tasks_done_recently
        return response
    
class BoardTaskListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, board_id):
        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            return Response({"detail": "Board not found"}, status=status.HTTP_404_NOT_FOUND)

        tasks = Task.objects.filter(board=board).select_related('assigned_to', 'reviewer')
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
    
class TaskCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data.copy()

        serializer = TaskSerializer(data=data)
        if serializer.is_valid():
            task = serializer.save()
            response_serializer = TaskSerializer(task)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class TaskDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response({"detail": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response({"detail": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response({"detail": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        task_id = self.kwargs.get('task_pk')
        return Comment.objects.filter(task_id=task_id)

    def perform_create(self, serializer):
        task_id = self.kwargs.get('task_pk')
        serializer.save(task_id=task_id, author=self.request.user)

class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        task_id = self.kwargs.get('task_id')
        return Comment.objects.filter(task_id=task_id)

    def perform_create(self, serializer):
        task_id = self.kwargs.get('task_id')
        serializer.save(task_id=task_id, author=self.request.user)

class CommentDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, task_id, pk):
        try:
            comment = Comment.objects.get(pk=pk, task_id=task_id)
        except Comment.DoesNotExist:
            return Response({"detail": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if comment.author != request.user:
            return Response({"detail": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)
        
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class DashboardView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        now = timezone.now()

        two_weeks_ago = now - timedelta(days=14)
        tasks_done_recently = Task.objects.filter(
            status='done',
            updated_at__gte=two_weeks_ago
        ).count()

        tickets_distribution = {
            'to_do': Task.objects.filter(status='to-do').count(),
            'in_progress': Task.objects.filter(status='in-progress').count(),
            'review': Task.objects.filter(status='review').count(),
            'done': Task.objects.filter(status='done').count(),
        }

        urgent_tasks = Task.objects.filter(
            status='to-do',
            due_date__isnull=False
        ).order_by('due_date')

        next_deadline = None
        if urgent_tasks.exists():
            next_task = urgent_tasks.first()
            next_deadline = {
                "id": next_task.id,
                "title": next_task.title,
                "due_date": next_task.due_date
            }

        urgent_to_do = {
            "count": urgent_tasks.count(),
            "next_deadline": next_deadline
        }

        your_tasks = Task.objects.filter(assigned_to=user).order_by('-updated_at')[:5]
        your_tasks_data = TaskSerializer(your_tasks, many=True).data

        tasks_insights = {
            "assigned_to_you": Task.objects.filter(assigned_to=user).count(),
            "to_review": Task.objects.filter(reviewer=user).count(),
        }

        data = {
            "tasks_done_recently": tasks_done_recently,
            "tickets_distribution": tickets_distribution,
            "urgent_to_do": urgent_to_do,
            "your_tasks": your_tasks_data,
            "tasks_insights": tasks_insights,
        }

        return Response(data, status=status.HTTP_200_OK)