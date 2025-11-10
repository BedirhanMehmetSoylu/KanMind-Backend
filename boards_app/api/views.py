from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.db.models import Q

from .models import Board
from .serializers import BoardListSerializer, BoardDetailSerializer, BoardUpdateSerializer
from task_app.api.serializers import Task

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

        serializer = BoardListSerializer(boards, many=True)
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

        serializer = BoardListSerializer(board)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class BoardDetailView(APIView):
    """
    Retrieve, update or delete a specific board.
    Access is granted if the user is the creator, member,
    assigned to a task or reviewer of a task.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """Return board details or proper error."""
        try: board = Board.objects.get(pk=pk)
        except Board.DoesNotExist:
            return Response({"detail": "Board not found."}, status=404)
        u = request.user
        if u != board.created_by and u not in board.members.all() and not Task.objects.filter(board=board, assigned_to=u).exists() and not Task.objects.filter(board=board, reviewer=u).exists():
            return Response({"detail": "Forbidden. Must be member or owner of the Board."}, status=403)
        return Response(BoardDetailSerializer(board).data, status=200)

    def patch(self, request, pk):
        """
        Update a board's title or members.
        Only owner or members can modify.
        Returns 200, 400, 403 or 404.
        """
        try: board = Board.objects.get(pk=pk)
        except Board.DoesNotExist: return Response({"detail": "Board not found."}, status=404)
        if request.user != board.created_by and request.user not in board.members.all():
            return Response({"detail": "Forbidden. Must be owner or member."}, status=403)
        title, members = request.data.get("title") or request.data.get("name"), request.data.get("members")
        if title: board.name = title
        if members is not None:
            if not isinstance(members, list) or not all(isinstance(i, int) for i in members):
                return Response({"detail": "Invalid members format."}, status=400)
            valid = User.objects.filter(id__in=members)
            if valid.count() != len(members):
                return Response({"detail": "One or more member IDs are invalid."}, status=400)
            board.members.set(valid)
        board.save()
        return Response(BoardUpdateSerializer(board).data, status=200)
    
    def delete(self, request, pk):
        """
        Delete a board (only creator allowed).
        Returns 204, 403 or 404.
        """
        try: board = Board.objects.get(pk=pk)
        except Board.DoesNotExist:
            return Response({"detail": "Board not found."}, status=404)
        if request.user != board.created_by:
            return Response({"detail": "Forbidden. Only owner can delete."}, status=403)
        board.delete()
        return Response(status=204)