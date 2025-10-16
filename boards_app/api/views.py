from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .models import Board
from .serializers import BoardSerializer

User = get_user_model()


class BoardListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        boards = Board.objects.filter(created_by=request.user)
        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data)

    def post(self, request):
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
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            board = Board.objects.get(pk=pk, created_by=request.user)
        except Board.DoesNotExist:
            return Response({"detail": "Board not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = BoardSerializer(board)
        return Response(serializer.data)

    def patch(self, request, pk):
        try:
            board = Board.objects.get(pk=pk, created_by=request.user)
        except Board.DoesNotExist:
            return Response({"detail": "Board not found"}, status=status.HTTP_404_NOT_FOUND)

        new_title = request.data.get("title") or request.data.get("name")
        if new_title:
            board.name = new_title

        member_ids = request.data.get("members", None)
        if member_ids is not None:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            valid_members = User.objects.filter(id__in=member_ids)
            board.members.set(valid_members)

        board.save()
        serializer = BoardSerializer(board)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, pk):
        try:
            board = Board.objects.get(pk=pk, created_by=request.user)
        except Board.DoesNotExist:
            return Response({"detail": "Board not found"}, status=status.HTTP_404_NOT_FOUND)

        board.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    
class AssignedTasksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # TODO: später durch echte Tasks ersetzen
        tasks = []
        return Response(tasks)