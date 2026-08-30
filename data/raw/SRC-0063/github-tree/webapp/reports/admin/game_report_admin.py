from django.contrib import admin
from django.utils.html import format_html

from reports.models import GameReport, GameReportAdvice
from unfold.admin import ModelAdmin, TabularInline

from common.admin.utils import (
    COLOR_GREEN,
    COLOR_ORANGE,
    render_colored_text,
    render_count,
    render_two_line_info,
)


class GameReportAdviceInline(TabularInline):
    """게임 레포트 조언 인라인"""

    model = GameReportAdvice
    extra = 0
    can_delete = False
    show_change_link = True

    fields = (
        "game",
        "title",
        "description",
        "error_message",
        "created_at",
    )
    readonly_fields = (
        "game",
        "error_message",
        "created_at",
    )

    def has_add_permission(self, request, obj=None):
        """생성 불가 (서비스를 통해서만 생성)"""
        return False


@admin.register(GameReport)
class GameReportAdmin(ModelAdmin):
    """게임 레포트 관리자 페이지"""

    list_display = (
        "id",
        "report_info",
        "game_info",
        "is_up_to_date_display",
        "advice_count_display",
        "updated_at",
    )
    list_filter = (
        "game",
        "updated_at",
    )
    search_fields = (
        "report__user__username",
        "report__user__email",
        "report__child__name",
        "game__name",
    )
    ordering = ("-updated_at",)
    date_hierarchy = "updated_at"
    readonly_fields = (
        "report",
        "game",
        "last_reflected_session",
        "meta",
        "created_at",
        "updated_at",
    )
    autocomplete_fields = ("report", "game", "last_reflected_session")

    fieldsets = (
        (
            "기본 정보",
            {
                "fields": (
                    "report",
                    "game",
                    "last_reflected_session",
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

    inlines = [GameReportAdviceInline]

    list_per_page = 25
    show_full_result_count = True

    def report_info(self, obj):
        """레포트 정보 표시"""
        if obj.report:
            return render_two_line_info(
                f"{obj.report.user.username} - {obj.report.child.name}",
                f"Report #{obj.report.id}",
            )
        return "-"

    report_info.short_description = "레포트"
    report_info.admin_order_field = "report__user__username"

    def game_info(self, obj):
        """게임 정보 표시"""
        if obj.game:
            return format_html("<strong>{}</strong>", obj.game.name)
        return "-"

    game_info.short_description = "게임"
    game_info.admin_order_field = "game__name"

    def is_up_to_date_display(self, obj):
        """최신 반영 여부 표시"""
        is_current = obj.is_up_to_date()
        if is_current:
            return render_colored_text("✓ 최신", COLOR_GREEN)
        return render_colored_text("⚠ 업데이트 필요", COLOR_ORANGE)

    is_up_to_date_display.short_description = "최신 반영"

    def advice_count_display(self, obj):
        """조언 개수 표시"""
        count = len(obj.advices.all())
        return render_count(count)

    advice_count_display.short_description = "조언 수"

    def get_queryset(self, request):
        """쿼리셋 최적화"""
        queryset = super().get_queryset(request)
        return queryset.select_related(
            "report__user",
            "report__child",
            "game",
            "last_reflected_session",
        ).prefetch_related("advices")

    def has_add_permission(self, request):
        """생성 불가 (서비스를 통해서만 생성)"""
        return False

    def has_change_permission(self, request, obj=None):
        """조회 및 Inline 수정 가능"""
        return True

    def has_delete_permission(self, request, obj=None):
        """삭제는 슈퍼유저만 가능"""
        return request.user.is_superuser
