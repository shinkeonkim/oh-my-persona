from django.contrib import admin
from meme.models.memo import Memo
from unfold.admin import ModelAdmin


@admin.register(Memo)
class MemoAdmin(ModelAdmin):
    """
    Admin interface for managing memos.
    """

    list_display = ("id", "creator", "meme", "content", "created_at", "updated_at")
    search_fields = ("content",)
    list_filter = ("creator", "meme")
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
