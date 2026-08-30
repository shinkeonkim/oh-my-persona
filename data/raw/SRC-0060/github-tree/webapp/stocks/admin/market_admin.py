from django.contrib import admin

from stocks.models import Market
from unfold.admin import ModelAdmin


@admin.register(Market)
class MarketAdmin(ModelAdmin):
  list_display = ("name", "code", "country", "created_at", "updated_at")
  search_fields = ("name", "code")
  list_filter = ("country", "code")
  ordering = ("country", "code")
  autocomplete_fields = ()
  list_filter_submit = True
  list_filter_sheet = False
