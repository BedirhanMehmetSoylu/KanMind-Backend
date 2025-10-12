from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Board(models.Model):
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='created_boards'
    )
    members = models.ManyToManyField(
        User, related_name='boards', blank=True
    )

    def __str__(self):
        return self.name