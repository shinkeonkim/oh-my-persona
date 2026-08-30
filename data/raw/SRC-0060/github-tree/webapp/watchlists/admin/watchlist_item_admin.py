from django.contrib import admin

from unfold.admin import ModelAdmin
from watchlists.models import WatchlistItem


@admin.register(WatchlistItem)
class WatchlistItemAdmin(ModelAdmin):
  list_display = ("watchlist", "stock", "notes_preview", "created_at")
  search_fields = (
    "watchlist__name",
    "watchlist__user__email",
    "watchlist__user__username",
    "stock__name",
    "stock__code",
  )
  list_filter = ("watchlist", "stock", "created_at")
  autocomplete_fields = ("watchlist", "stock")
  readonly_fields = ("created_at", "updated_at")
  ordering = ("-created_at", )
  list_filter_submit = True
  list_filter_sheet = False

  def notes_preview(self, obj):
    if not obj.notes:
      return ""
    return (obj.notes[:50] + "...") if len(obj.notes) > 50 else obj.notes

  notes_preview.short_description = "메모"
