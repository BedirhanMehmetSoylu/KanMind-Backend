from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Board(models.Model):
    """
    Represents a collaborative project board that can have multiple members and tasks.
    
    Attributes:
        name (str): The name of the board.
        created_by (User): The user who created the board.
        members (QuerySet[User]): Users who are members of the board.
    """
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='created_boards'
    )
    members = models.ManyToManyField(
        User, related_name='boards', blank=True
    )

    def __str__(self):
        """Return the board’s name as string representation."""
        return self.name