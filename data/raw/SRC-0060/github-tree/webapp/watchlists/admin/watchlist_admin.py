from django.contrib import admin

from unfold.admin import ModelAdmin, TabularInline
from watchlists.models import Watchlist, WatchlistItem


class WatchlistItemInline(TabularInline):
  """관심목록 내 아이템 인라인"""
  model = WatchlistItem
  extra = 0
  fields = ("stock", "notes", "created_at")
  autocomplete_fields = ("stock", )
  readonly_fields = ("created_at", )


@admin.register(Watchlist)
class WatchlistAdmin(ModelAdmin):
  list_display = ("name", "user", "item_count", "created_at")
  search_fields = (
    "name",
    "description",
    "user__email",
    "user__username",
  )
  list_filter = ("user", "created_at")
  autocomplete_fields = ("user", )
  readonly_fields = ("created_at", "updated_at")
  ordering = ("-created_at", )
  list_filter_submit = True
  list_filter_sheet = False
  inlines = [WatchlistItemInline]

  def item_count(self, obj):
    return obj.items.count()

  item_count.short_description = "아이템 수"
