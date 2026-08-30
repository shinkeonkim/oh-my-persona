from django.contrib import admin
from django.utils.html import format_html

from games.models import GameSession
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import ChoicesDropdownFilter


@admin.register(GameSession)
class GameSessionAdmin(ModelAdmin):
    """게임 세션 관리자 페이지"""

    list_display = (
        "id",
        "parent_info",
        "child_info",
        "game_info",
        "status_display",
        "current_round",
        "current_score",
        "started_at",
        "ended_at",
    )
    list_filter = (
        ("status", ChoicesDropdownFilter),
        "game",
        "started_at",
        "ended_at",
        "created_at",
    )
    search_fields = (
        "id",
        "parent__email",
        "parent__username",
        "child__name",
        "game__name",
        "game__code",
    )
    ordering = ("-started_at",)
    date_hierarchy = "started_at"
    readonly_fields = (
        "id",
        "parent",
        "child",
        "game",
        "status",
        "current_round",
        "current_score",
        "started_at",
        "ended_at",
        "meta",
        "created_at",
        "updated_at",
    )
    autocomplete_fields = ("parent", "child", "game")

    fieldsets = (
        (
            "세션 정보",
            {
                "fields": (
                    "id",
                    "parent",
                    "child",
                    "game",
                    "status",
                )
            },
        ),
        (
            "진행 상황",
            {
                "fields": (
                    "current_round",
                    "current_score",
                    "started_at",
                    "ended_at",
                )
            },
        ),
        (
            "메타데이터",
            {
                "fields": ("meta",),
                "classes": ("collapse",),
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

    def parent_info(self, obj):
        """부모 정보 표시"""
        if obj.parent:
            return format_html(
                "<strong>{}</strong><br/><small>{}</small>",
                obj.parent.username or obj.parent.email,
                obj.parent.email,
            )
        return "-"

    parent_info.short_description = "부모"
    parent_info.admin_order_field = "parent__username"

    def child_info(self, obj):
        """아동 정보 표시"""
        if obj.child:
            return format_html(
                "<strong>{}</strong>",
                obj.child.name,
            )
        return "-"

    child_info.short_description = "아동"
    child_info.admin_order_field = "child__name"

    def game_info(self, obj):
        """게임 정보 표시"""
        if obj.game:
            return format_html(
                "<strong>{}</strong><br/><small>{}</small>",
                obj.game.name,
                obj.game.code,
            )
        return "-"

    game_info.short_description = "게임"
    game_info.admin_order_field = "game__name"

    def status_display(self, obj):
        """상태 표시 (색상 포함)"""
        color_map = {
            "STARTED": "#2196F3",  # Blue
            "COMPLETED": "#4CAF50",  # Green
            "GAME_OVER": "#FF9800",  # Orange
            "FORFEIT": "#F44336",  # Red
        }
        color = color_map.get(obj.status, "#000000")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_display.short_description = "상태"
    status_display.admin_order_field = "status"

    def get_queryset(self, request):
        """쿼리셋 최적화"""
        queryset = super().get_queryset(request)
        return queryset.select_related("parent", "child", "game")

    def has_add_permission(self, request):
        """생성 불가 (API를 통해서만 생성)"""
        return False

    def has_change_permission(self, request, obj=None):
        """수정 불가 (읽기 전용)"""
        return False

    def has_delete_permission(self, request, obj=None):
        """삭제는 슈퍼유저만 가능"""
        return request.user.is_superuser
