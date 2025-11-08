from django.urls import path

from .views import AssignedTasksView, ReviewingTasksView, BoardTaskListView, TaskCreateView, TaskDetailView, CommentListCreateView, CommentDeleteView, DashboardView

urlpatterns = [
    path('tasks/assigned-to-me/', AssignedTasksView.as_view(), name='tasks_assigned'),
    path('tasks/reviewing/', ReviewingTasksView.as_view(), name='tasks_reviewing'),
    path('boards/<int:board_id>/tasks/', BoardTaskListView.as_view(), name='board_tasks'),
    path('tasks/', TaskCreateView.as_view(), name='task_create'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task_detail'),
    path('tasks/<int:task_id>/comments/', CommentListCreateView.as_view(), name='task_comments'),
    path('tasks/<int:task_id>/comments/<int:pk>/', CommentDeleteView.as_view(), name='comment_delete'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]
