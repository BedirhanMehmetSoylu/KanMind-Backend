from django.urls import path
from .views import BoardListView, BoardDetailView

urlpatterns = [
    path('boards/', BoardListView.as_view(), name='boards'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board_detail'),
]
