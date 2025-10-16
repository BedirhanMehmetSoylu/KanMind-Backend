from django.urls import path
from .views import BoardListView, BoardDetailView, AssignedTasksView

urlpatterns = [
    path('boards/', BoardListView.as_view(), name='boards'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board_detail'),
    path('tasks/assigned-to-me/', AssignedTasksView.as_view(), name='tasks_assigned'),
]
