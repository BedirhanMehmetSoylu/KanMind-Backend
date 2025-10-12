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
    
class AssignedTasksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # TODO: später durch echte Tasks ersetzen
        tasks = []
        return Response(tasks)