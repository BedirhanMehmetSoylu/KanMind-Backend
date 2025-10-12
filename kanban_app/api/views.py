from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

"""
Views for board and task endpoints.

Currently return empty lists (no data yet).
Will be connected to database models in a later step.
"""

class BoardListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # TODO: Replace with real board data once the model is implemented
        return Response([], status=status.HTTP_200_OK)


class AssignedTasksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # TODO: Replace with real task data once the model is implemented
        return Response([], status=status.HTTP_200_OK)
