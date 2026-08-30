from bookmark.models.bookmarking import Bookmarking
from django.contrib import admin
from unfold.admin import ModelAdmin


class BookmarkingAdmin(ModelAdmin):
    list_display = ("bookmark", "meme")
    search_fields = ("bookmark__title", "meme__title")
    list_filter = ("bookmark", "meme")

    fields = (
        "bookmark",
        "meme",
    )


admin.site.register(Bookmarking, BookmarkingAdmin)
