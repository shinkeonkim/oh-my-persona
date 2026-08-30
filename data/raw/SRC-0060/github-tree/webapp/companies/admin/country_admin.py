from django.contrib import admin

from unfold.admin import ModelAdmin

from companies.models import Country


@admin.register(Country)
class CountryAdmin(ModelAdmin):
  """국가 Admin"""

  list_display = [
    "code",
    "name",
    "created_at",
    "updated_at",
  ]

  search_fields = [
    "code",
    "name",
  ]

  ordering = ["code"]

  readonly_fields = [
    "created_at",
    "updated_at",
  ]

  list_filter_submit = True
  list_filter_sheet = False
