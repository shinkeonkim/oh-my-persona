from django.contrib import admin

from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import ChoicesDropdownFilter

from file_managers.models import Image


@admin.register(Image)
class ImageAdmin(ModelAdmin):
  list_display = ("id", "owner", "image_type", "file", "created_at", "updated_at")
  list_filter = (
    ("image_type", ChoicesDropdownFilter),
    "owner",
    "created_at",
    "updated_at",
  )
  search_fields = ("owner__email", "owner__username", "file")
  ordering = ("-created_at", )
  date_hierarchy = "created_at"
  list_filter_submit = True
  list_filter_sheet = False
