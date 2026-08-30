from django.contrib import admin

from reports.models import ReportPin
from unfold.admin import ModelAdmin


@admin.register(ReportPin)
class ReportPinAdmin(ModelAdmin):
    list_display = (
        "user",
        "enabled_at",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "enabled_at",
        "created_at",
    )
    search_fields = ("user__email",)
    readonly_fields = (
        "pin_hash",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)

    fields = (
        "user",
        "pin_hash",
        "enabled_at",
        "created_at",
        "updated_at",
    )

    actions = ()
