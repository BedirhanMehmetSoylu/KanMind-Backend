from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Board

User = get_user_model()


class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']


class BoardSerializer(serializers.ModelSerializer):
    created_by = UserMiniSerializer(read_only=True)
    members = UserMiniSerializer(many=True, read_only=True)
    title = serializers.CharField(source='name', read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'name', 'title', 'created_by', 'members']