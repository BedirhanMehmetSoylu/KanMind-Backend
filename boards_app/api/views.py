from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.db.models import Q

from .models import Board
from .serializers import BoardSerializer
from task_app.api.models import Task
from task_app.api.serializers import TaskSerializer

User = get_user_model()


class BoardListView(APIView):
    """
    Handles retrieving all boards accessible to the authenticated user,
    and creating new boards.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Return a list of boards where the user is:
        - Creator
        - Member
        - Assigned to a task
        - Reviewer of a task
        """
        user = request.user

        boards = Board.objects.filter(
            Q(created_by=user) |
            Q(members=user) |
            Q(tasks__assigned_to=user) |
            Q(tasks__reviewer=user)
        ).distinct()

        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Create a new board with the current user as creator.
        Members can be added by providing a list of user IDs.
        """
        name = request.data.get('name') or request.data.get('title')
        member_ids = request.data.get('members', [])

        if not name:
            return Response({"detail": "Board name is required"}, status=status.HTTP_400_BAD_REQUEST)

        board = Board.objects.create(name=name, created_by=request.user)

        valid_members = User.objects.filter(id__in=member_ids)
        board.members.add(*valid_members)

        serializer = BoardSerializer(board)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class BoardDetailView(APIView):
    """
    Retrieve, update or delete a specific board.
    Access is granted if the user is the creator, member,
    assigned to a task or reviewer of a task.
    """

    permission_classes = [IsAuthenticated]

    def get_board(self, pk, user):
        """Helper to safely fetch board with access check."""
        return Board.objects.filter(
            Q(id=pk),
            Q(created_by=user) |
            Q(members=user) |
            Q(tasks__assigned_to=user) |
            Q(tasks__reviewer=user)
        ).distinct().first()

    def get(self, request, pk):
        """Return details of a specific board and its tasks."""
        board = self.get_board(pk, request.user)
        if not board:
            return Response({"detail": "Board not found or no access"}, status=status.HTTP_404_NOT_FOUND)

        data = BoardSerializer(board).data
        data['tasks'] = TaskSerializer(Task.objects.filter(board=board), many=True).data
        return Response(data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        """Update a board's title or members (only allowed for creator)."""
        try:
            board = Board.objects.get(pk=pk, created_by=request.user)
        except Board.DoesNotExist:
            return Response({"detail": "Board not found"}, status=status.HTTP_404_NOT_FOUND)

        self._update_board(board, request.data)
        serializer = BoardSerializer(board)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def _update_board(self, board, data):
        """Helper to update board title and members."""
        title = data.get("title") or data.get("name")
        if title:
            board.name = title

        member_ids = data.get("members")
        if member_ids is not None:
            valid_members = User.objects.filter(id__in=member_ids)
            board.members.set(valid_members)

        board.save()

    def delete(self, request, pk):
        """Delete a board (only allowed for creator)."""
        try:
            board = Board.objects.get(pk=pk, created_by=request.user)
        except Board.DoesNotExist:
            return Response({"detail": "Board not found"}, status=status.HTTP_404_NOT_FOUND)

        board.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)