from django.contrib import admin

from unfold.admin import ModelAdmin

from users.models import User


@admin.register(User)
class UserAdmin(ModelAdmin):
  list_display = (
    "email",
    "username",
    "is_active",
    "is_staff",
    "is_superuser",
  )
  list_filter = (
    "is_active",
    "is_staff",
    "is_superuser",
    "created_at",
  )
  search_fields = (
    "email",
    "username",
  )
  readonly_fields = (
    "is_active",
    "is_staff",
    "is_superuser",
    "created_at",
    "updated_at",
  )
  ordering = ("-created_at", )

  fields = (
    "email",
    "username",
    "is_active",
    "is_staff",
    "is_superuser",
    "created_at",
    "updated_at",
  )

  actions = ()
