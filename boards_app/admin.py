"""
Admin configuration for boards_app models.

Registers Board model with custom display and member count
for the Django admin interface.
"""

from django.contrib import admin

from boards_app.api.models import Board

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    """Admin view for Board model with custom display columns."""
    list_display = ('id', 'name', 'created_by', 'member_count')
    search_fields = ('name', 'created_by__username')
    list_filter = ('created_by',)
    
    def member_count(self, obj):
        """Return the number of members in the board."""
        return obj.members.count()
    member_count.short_description = 'Members'