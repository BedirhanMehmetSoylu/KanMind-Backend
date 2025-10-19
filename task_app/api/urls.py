from django.urls import path
from .views import AssignedTasksView, ReviewingTasksView, BoardTaskListView, TaskCreateView, TaskDetailView

urlpatterns = [
    path('tasks/assigned-to-me/', AssignedTasksView.as_view(), name='tasks_assigned'),
    path('tasks/reviewing/', ReviewingTasksView.as_view(), name='tasks_reviewing'),
    path('boards/<int:board_id>/tasks/', BoardTaskListView.as_view(), name='board_tasks'),
    path('tasks/', TaskCreateView.as_view(), name='task_create'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task_detail'),
]
