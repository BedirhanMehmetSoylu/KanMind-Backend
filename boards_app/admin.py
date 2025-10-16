from django.contrib import admin
from boards_app.api.models import Board

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_by', 'member_count')
    search_fields = ('name', 'created_by__username')
    list_filter = ('created_by',)
    
    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Members'