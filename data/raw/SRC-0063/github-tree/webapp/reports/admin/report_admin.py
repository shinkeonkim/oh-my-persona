from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils.html import format_html

from reports.admin.views import SendReportEmailView
from reports.models import GameReport, Report
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import action

from common.admin.utils import (
    COLOR_GREEN,
    COLOR_GREY,
    COLOR_ORANGE,
    REPORT_STATUS_COLORS,
    render_badge,
    render_colored_score,
    render_colored_text,
    render_count,
    render_two_line_info,
)


class GameReportInline(TabularInline):
    """게임 레포트 인라인"""

    model = GameReport
    extra = 0
    can_delete = False
    show_change_link = True

    fields = (
        "game",
        "last_reflected_session",
        "is_up_to_date_display",
        "view_details_link",
        "updated_at",
    )
    readonly_fields = (
        "game",
        "last_reflected_session",
        "is_up_to_date_display",
        "view_details_link",
        "updated_at",
    )

    def is_up_to_date_display(self, obj):
        """최신 반영 여부 표시"""
        if obj.pk:
            is_current = obj.is_up_to_date()
            if is_current:
                return render_colored_text("✓ 최신", COLOR_GREEN)
            return render_colored_text("⚠ 업데이트 필요", COLOR_ORANGE)
        return "-"

    is_up_to_date_display.short_description = "최신 반영"

    def view_details_link(self, obj):
        """상세 보기 링크"""
        if obj.pk:
            url = reverse("admin:reports_gamereport_change", args=[obj.pk])
            return format_html(
                '<a href="{}" style="color: #2196F3; text-decoration: none; font-weight: 500;">📋 상세보기</a>',
                url,
            )
        return "-"

    view_details_link.short_description = "상세"

    def has_add_permission(self, request, obj=None):
        """생성 불가 (서비스를 통해서만 생성)"""
        return False


@admin.register(Report)
class ReportAdmin(ModelAdmin):
    """레포트 관리자 페이지"""

    list_display = (
        "id",
        "user_info",
        "child_info",
        "concentration_score_display",
        "status_display",
        "game_reports_count",
        "updated_at",
    )
    list_filter = (
        "status",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "user__username",
        "user__email",
        "child__name",
    )
    ordering = ("-updated_at",)
    date_hierarchy = "updated_at"
    readonly_fields = (
        "user",
        "child",
        "concentration_score",
        "status",
        "created_at",
        "updated_at",
    )
    autocomplete_fields = ("user", "child")
    actions = []
    actions_detail = ["send_email_action"]

    fieldsets = (
        (
            "기본 정보",
            {
                "fields": (
                    "user",
                    "child",
                )
            },
        ),
        (
            "레포트 상세",
            {
                "fields": (
                    "concentration_score",
                    "status",
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

    inlines = [GameReportInline]

    list_per_page = 25
    show_full_result_count = True

    def user_info(self, obj):
        """사용자 정보 표시"""
        if obj.user:
            return render_two_line_info(obj.user.username, obj.user.email)
        return "-"

    user_info.short_description = "사용자"
    user_info.admin_order_field = "user__username"

    def child_info(self, obj):
        """아동 정보 표시"""
        if obj.child:
            return format_html("<strong>{}</strong>", obj.child.name)
        return "-"

    child_info.short_description = "아동"
    child_info.admin_order_field = "child__name"

    def concentration_score_display(self, obj):
        """집중력 점수 표시 (색상 포함)"""
        return render_colored_score(obj.concentration_score)

    concentration_score_display.short_description = "집중력 점수"
    concentration_score_display.admin_order_field = "concentration_score"

    def status_display(self, obj):
        """상태 표시 (뱃지 스타일)"""
        color = REPORT_STATUS_COLORS.get(obj.status, COLOR_GREY)
        return render_badge(obj.get_status_display(), color)

    status_display.short_description = "상태"
    status_display.admin_order_field = "status"

    def game_reports_count(self, obj):
        """게임 레포트 개수 표시"""
        count = obj.game_reports.count()
        return render_count(count)

    game_reports_count.short_description = "게임 레포트 수"

    def get_queryset(self, request):
        """쿼리셋 최적화"""
        queryset = super().get_queryset(request)
        return queryset.select_related("user", "child").prefetch_related("game_reports__advices")

    def has_add_permission(self, request):
        """생성 불가 (서비스를 통해서만 생성)"""
        return False

    def has_change_permission(self, request, obj=None):
        """수정 불가 (읽기 전용)"""
        return False

    def has_delete_permission(self, request, obj=None):
        """삭제는 슈퍼유저만 가능"""
        return request.user.is_superuser

    def get_urls(self):
        """커스텀 URL 추가"""
        urls = super().get_urls()
        custom_urls = [
            path(
                "<path:object_id>/send-email/",
                self.admin_site.admin_view(SendReportEmailView.as_view(model_admin=self)),
                name="reports_report_send_email",
            ),
        ]
        return custom_urls + urls

    @action(description="이메일 전송", url_path="send-email-redirect")
    def send_email_action(self, request, object_id):
        """
        이메일 전송 페이지로 리다이렉트하는 액션

        Detail 페이지의 액션 버튼으로 표시되며,
        클릭 시 커스텀 페이지로 이동합니다.
        """
        url = reverse("admin:reports_report_send_email", args=[object_id])
        return redirect(url)
