from django.contrib import admin

from games.models import Game
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import ChoicesDropdownFilter


@admin.register(Game)
class GameAdmin(ModelAdmin):
    """게임 관리자 페이지"""

    list_display = (
        "id",
        "code",
        "name",
        "max_round",
        "is_active",
        "created_at",
        "updated_at",
    )
    list_filter = (
        ("code", ChoicesDropdownFilter),
        "is_active",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "code",
        "name",
    )
    ordering = ("id",)
    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "게임 정보",
            {
                "fields": (
                    "code",
                    "name",
                    "max_round",
                    "is_active",
                )
            },
        ),
        (
            "시스템 정보",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    list_per_page = 25
    show_full_result_count = True
