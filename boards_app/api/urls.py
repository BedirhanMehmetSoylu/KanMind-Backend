from django.urls import path
from .views import BoardListView, AssignedTasksView

urlpatterns = [
    path('boards/', BoardListView.as_view(), name='boards'),
    path('tasks/assigned-to-me/', AssignedTasksView.as_view(), name='tasks_assigned'),
]
