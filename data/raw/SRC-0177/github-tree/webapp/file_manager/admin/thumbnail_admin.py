from django.contrib import admin
from file_manager.models.thumbnail import Thumbnail
from unfold.admin import ModelAdmin


@admin.register(Thumbnail)
class ThumbnailAdmin(ModelAdmin):
    list_display = ("name", "preview_image", "url", "file", "web_url")
    search_fields = (
        "web_url",
        "name",
    )
    list_filter = ("file",)

    fields = ("name", "file", "web_url", "url")
    readonly_fields = ("url",)
