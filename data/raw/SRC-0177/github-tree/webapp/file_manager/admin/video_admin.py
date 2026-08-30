from django.contrib import admin
from file_manager.models import Video
from unfold.admin import ModelAdmin


@admin.register(Video)
class VideoAdmin(ModelAdmin):
    list_display = ("name", "file", "link", "link_type")
    search_fields = (
        "file",
        "name",
        "link",
        "link_type",
    )
    list_filter = (
        "name",
        "link",
        "link_type",
    )

    fields = (
        "name",
        "file",
        "link",
        "link_type",
    )
    readonly_fields = ("type",)
