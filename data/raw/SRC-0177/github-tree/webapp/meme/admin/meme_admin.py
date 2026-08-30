from django.contrib import admin
from meme.models import Meme, MemeCounter
from tag.models import MemeTagging
from unfold.admin import ModelAdmin, TabularInline


class MemeTaggingInline(TabularInline):
    model = MemeTagging
    extra = 1
    max_num = 10
    fields = ["tag"]


class MemeCounterInline(TabularInline):
    model = MemeCounter
    extra = 1
    fields = ["bookmarking_users_count", "bookmarkings_count"]
    readonly_fields = ["bookmarking_users_count", "bookmarkings_count"]


@admin.register(Meme)
class MemeAdmin(ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is None:
            form.base_fields["creator"].initial = request.user
        return form

    def reset_all_counters(self, request, queryset):
        for meme in queryset:
            meme.reset_all_counters()
        self.message_user(request, "All counters have been reset.")

    def publish(self, request, queryset):
        for meme in queryset:
            meme.publish()
        self.message_user(request, "All memes have been published.")

    def archive(self, request, queryset):
        for meme in queryset:
            meme.archive()
        self.message_user(request, "All memes have been archived.")

    def undo_archive(self, request, queryset):
        for meme in queryset:
            meme.undo_archive()
        self.message_user(request, "All memes have been unarchived.")

    def undo_publish(self, request, queryset):
        for meme in queryset:
            meme.undo_publish()
        self.message_user(request, "All memes have been unpublished.")

    list_display = ("title", "type", "created_at", "updated_at")
    list_filter = ("title", "type")
    search_fields = ("title", "description")
    ordering = ("-created_at", "title")
    inlines = [MemeTaggingInline, MemeCounterInline]
    fields = [
        "title",
        "type",
        "thumbnail",
        "audio",
        "video",
        "description",
        "original_title",
        "original_link",
        "published_at",
        "archived_at",
        "creator",
        "created_at",
        "updated_at",
    ]

    exclude = ["deleted_at"]
    readonly_fields = ["created_at", "updated_at", "deleted_at"]

    reset_all_counters.short_description = "Reset all counters"
    publish.short_description = "Publish"
    archive.short_description = "Archive"
    undo_archive.short_description = "Undo archive"
    undo_publish.short_description = "Undo publish"

    actions = [
        "reset_all_counters",
        "publish",
        "archive",
        "undo_archive",
        "undo_publish",
    ]
