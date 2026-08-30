from django.contrib import admin
from tag.models import TagCategory
from unfold.admin import ModelAdmin


@admin.register(TagCategory)
class TagCategoryAdmin(ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    list_filter = ()
    search_fields = ()
    ordering = ()

    exclude = ["deleted_at"]
    readonly_fields = ["created_at", "updated_at", "deleted_at"]
