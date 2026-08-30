from django.contrib import admin

from unfold.admin import ModelAdmin

from common.admin.utils import render_two_line_info
from users.models import BotToken


@admin.register(BotToken)
class BotTokenAdmin(ModelAdmin):
    """BOT 토큰 관리자 페이지"""

    list_display = (
        "id",
        "user_id_display",
        "created_at",
    )
    list_filter = ("created_at",)
    search_fields = (
        "user__username",
        "user__email",
        "token",
    )
    ordering = ("-created_at",)
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "기본 정보",
            {
                "fields": (
                    "user",
                    "token",
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

    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("user",)

    list_per_page = 25
    show_full_result_count = True

    def user_id_display(self, obj):
        """사용자 ID 및 정보 표시"""
        if obj.user:
            return render_two_line_info(f"#{obj.user.id}", obj.user.username)
        return "-"

    user_id_display.short_description = "사용자"
    user_id_display.admin_order_field = "user__id"

    def get_queryset(self, request):
        """쿼리셋 최적화"""
        queryset = super().get_queryset(request)
        return queryset.select_related("user")
