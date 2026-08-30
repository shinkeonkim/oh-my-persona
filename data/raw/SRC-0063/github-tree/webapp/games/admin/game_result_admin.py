from django.contrib import admin
from django.utils.html import format_html

from games.models import GameResult
from unfold.admin import ModelAdmin


@admin.register(GameResult)
class GameResultAdmin(ModelAdmin):
    """게임 결과 관리자 페이지"""

    list_display = (
        "id",
        "child_info",
        "game_info",
        "score_display",
        "wrong_count",
        "success_count",
        "round_count",
        "reaction_time_avg",
        "session_id",
        "created_at",
    )
    list_filter = (
        "game",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "child__name",
        "game__name",
        "game__code",
        "session__id",
    )
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    readonly_fields = (
        "session",
        "child",
        "game",
        "score",
        "wrong_count",
        "reaction_ms_sum",
        "round_count",
        "success_count",
        "meta",
        "created_at",
        "updated_at",
    )
    autocomplete_fields = ("session", "child", "game")

    fieldsets = (
        (
            "기본 정보",
            {
                "fields": (
                    "session",
                    "child",
                    "game",
                )
            },
        ),
        (
            "게임 결과",
            {
                "fields": (
                    "score",
                    "wrong_count",
                    "success_count",
                    "round_count",
                    "reaction_ms_sum",
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

    def score_display(self, obj):
        """점수 표시 (색상 포함)"""
        if obj.score >= 80:
            color = "#4CAF50"  # Green
        elif obj.score >= 60:
            color = "#FF9800"  # Orange
        else:
            color = "#F44336"  # Red

        return format_html(
            '<strong style="color: {}; font-size: 1.1em;">{}</strong>',
            color,
            obj.score,
        )

    score_display.short_description = "총점"
    score_display.admin_order_field = "score"

    def reaction_time_avg(self, obj):
        """평균 반응 시간 표시"""
        if obj.reaction_ms_sum is not None and obj.round_count is not None and obj.round_count > 0:
            avg_ms = obj.reaction_ms_sum / obj.round_count
            return format_html(
                "<span>{} ms</span>",
                int(avg_ms),
            )
        return "-"

    reaction_time_avg.short_description = "평균 반응시간"

    def session_id(self, obj):
        """세션 ID 표시 (짧게)"""
        if obj.session:
            session_id_str = str(obj.session.id)
            return format_html(
                "<small>{}</small>",
                session_id_str[:8] + "...",
            )
        return "-"

    session_id.short_description = "세션 ID"

    def get_queryset(self, request):
        """쿼리셋 최적화"""
        queryset = super().get_queryset(request)
        return queryset.select_related("session", "child", "game")

    def has_add_permission(self, request):
        """생성 불가 (API를 통해서만 생성)"""
        return False

    def has_change_permission(self, request, obj=None):
        """수정 불가 (읽기 전용)"""
        return False

    def has_delete_permission(self, request, obj=None):
        """삭제는 슈퍼유저만 가능"""
        return request.user.is_superuser
