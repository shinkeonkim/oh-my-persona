from unittest.mock import Mock

from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

import pytest
from games.models import Game
from reports.admin.report_admin import GameReportInline, ReportAdmin
from reports.choices import ReportStatusChoice
from reports.models import GameReport, Report

from users.models import Child

User = get_user_model()


@pytest.mark.django_db
class ReportAdminTests(TestCase):
    """ReportAdmin 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.factory = RequestFactory()
        self.admin_site = AdminSite()
        self.report_admin = ReportAdmin(Report, self.admin_site)

        # 사용자 생성
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="pass123",
        )

        # 자녀 생성
        self.child = Child.objects.create(
            parent=self.user,
            name="Test Child",
            birth_year=2020,
            gender="M",
        )

        # 게임 생성
        self.game = Game.objects.create(
            name="Test Game",
            code="TEST_GAME",
            max_round=10,
            is_active=True,
        )

        # 레포트 생성
        self.report = Report.objects.create(
            user=self.user,
            child=self.child,
            concentration_score=75,
            status=ReportStatusChoice.COMPLETED,
        )

        # 게임 레포트 생성
        self.game_report = GameReport.objects.create(
            report=self.report,
            game=self.game,
        )

    def test_list_display_configuration(self):
        """list_display 설정 테스트"""
        expected_fields = (
            "id",
            "user_info",
            "child_info",
            "concentration_score_display",
            "status_display",
            "game_reports_count",
            "updated_at",
        )
        self.assertEqual(self.report_admin.list_display, expected_fields)

    def test_list_filter_configuration(self):
        """list_filter 설정 테스트"""
        expected_filters = (
            "status",
            "created_at",
            "updated_at",
        )
        self.assertEqual(self.report_admin.list_filter, expected_filters)

    def test_search_fields_configuration(self):
        """search_fields 설정 테스트"""
        expected_fields = (
            "user__username",
            "user__email",
            "child__name",
        )
        self.assertEqual(self.report_admin.search_fields, expected_fields)

    def test_ordering_configuration(self):
        """ordering 설정 테스트"""
        self.assertEqual(self.report_admin.ordering, ("-updated_at",))

    def test_date_hierarchy_configuration(self):
        """date_hierarchy 설정 테스트"""
        self.assertEqual(self.report_admin.date_hierarchy, "updated_at")

    def test_readonly_fields_configuration(self):
        """readonly_fields 설정 테스트"""
        expected_fields = (
            "user",
            "child",
            "concentration_score",
            "status",
            "created_at",
            "updated_at",
        )
        self.assertEqual(self.report_admin.readonly_fields, expected_fields)

    def test_autocomplete_fields_configuration(self):
        """autocomplete_fields 설정 테스트"""
        expected_fields = ("user", "child")
        self.assertEqual(self.report_admin.autocomplete_fields, expected_fields)

    def test_actions_configuration(self):
        """actions 설정 테스트 (비어있어야 함)"""
        self.assertEqual(self.report_admin.actions, [])

    def test_list_per_page_configuration(self):
        """list_per_page 설정 테스트"""
        self.assertEqual(self.report_admin.list_per_page, 25)

    def test_show_full_result_count_configuration(self):
        """show_full_result_count 설정 테스트"""
        self.assertTrue(self.report_admin.show_full_result_count)

    def test_user_info_display_with_user(self):
        """user_info 메서드 테스트 (사용자가 있는 경우)"""
        result = self.report_admin.user_info(self.report)

        # HTML 형식 확인
        self.assertIn(self.user.username, result)
        self.assertIn(self.user.email, result)
        self.assertIn("<strong>", result)
        self.assertIn("<small>", result)

    def test_user_info_display_without_user(self):
        """user_info 메서드 테스트 (사용자가 없는 경우)"""
        mock_report = Mock(spec=Report)
        mock_report.user = None

        result = self.report_admin.user_info(mock_report)
        self.assertEqual(result, "-")

    def test_user_info_short_description(self):
        """user_info의 short_description 테스트"""
        self.assertEqual(self.report_admin.user_info.short_description, "사용자")

    def test_user_info_admin_order_field(self):
        """user_info의 admin_order_field 테스트"""
        self.assertEqual(self.report_admin.user_info.admin_order_field, "user__username")

    def test_child_info_display_with_child(self):
        """child_info 메서드 테스트 (자녀가 있는 경우)"""
        result = self.report_admin.child_info(self.report)

        # HTML 형식 확인
        self.assertIn(self.child.name, result)
        self.assertIn("<strong>", result)

    def test_child_info_display_without_child(self):
        """child_info 메서드 테스트 (자녀가 없는 경우)"""
        mock_report = Mock(spec=Report)
        mock_report.child = None

        result = self.report_admin.child_info(mock_report)
        self.assertEqual(result, "-")

    def test_child_info_short_description(self):
        """child_info의 short_description 테스트"""
        self.assertEqual(self.report_admin.child_info.short_description, "아동")

    def test_child_info_admin_order_field(self):
        """child_info의 admin_order_field 테스트"""
        self.assertEqual(self.report_admin.child_info.admin_order_field, "child__name")

    def test_concentration_score_display(self):
        """concentration_score_display 메서드 테스트"""
        result = self.report_admin.concentration_score_display(self.report)

        # 점수가 포함되어 있는지 확인
        self.assertIn("75", result)
        self.assertIn("<strong", result)  # style 속성이 있을 수 있으므로 닫는 태그는 체크 안 함

    def test_concentration_score_display_colors(self):
        """concentration_score_display의 색상 테스트"""
        # 80 이상 - 녹색
        self.report.concentration_score = 85
        result_high = self.report_admin.concentration_score_display(self.report)
        self.assertIn("#4CAF50", result_high)  # COLOR_GREEN

        # 60-79 - 주황색
        self.report.concentration_score = 70
        result_mid = self.report_admin.concentration_score_display(self.report)
        self.assertIn("#FF9800", result_mid)  # COLOR_ORANGE

        # 60 미만 - 빨간색
        self.report.concentration_score = 50
        result_low = self.report_admin.concentration_score_display(self.report)
        self.assertIn("#F44336", result_low)  # COLOR_RED

    def test_status_display(self):
        """status_display 메서드 테스트"""
        result = self.report_admin.status_display(self.report)

        # 뱃지 스타일 HTML 확인
        self.assertIn("<span", result)
        self.assertIn("background-color:", result)

    def test_status_display_short_description(self):
        """status_display의 short_description 테스트"""
        self.assertEqual(self.report_admin.status_display.short_description, "상태")

    def test_status_display_admin_order_field(self):
        """status_display의 admin_order_field 테스트"""
        self.assertEqual(self.report_admin.status_display.admin_order_field, "status")

    def test_game_reports_count(self):
        """game_reports_count 메서드 테스트"""
        result = self.report_admin.game_reports_count(self.report)

        # 카운트가 포함되어 있는지 확인
        self.assertIn("1", result)

    def test_game_reports_count_short_description(self):
        """game_reports_count의 short_description 테스트"""
        self.assertEqual(self.report_admin.game_reports_count.short_description, "게임 레포트 수")

    def test_get_queryset_optimization(self):
        """get_queryset 메서드의 최적화 테스트"""
        request = self.factory.get("/admin/reports/report/")
        request.user = self.user

        queryset = self.report_admin.get_queryset(request)

        # select_related와 prefetch_related 확인
        self.assertIn("user", queryset.query.select_related)
        self.assertIn("child", queryset.query.select_related)

    def test_has_add_permission_false(self):
        """생성 권한 테스트 (불가능해야 함)"""
        request = self.factory.get("/admin/reports/report/")
        request.user = self.user

        self.assertFalse(self.report_admin.has_add_permission(request))

    def test_has_change_permission_false(self):
        """수정 권한 테스트 (불가능해야 함)"""
        request = self.factory.get("/admin/reports/report/")
        request.user = self.user

        self.assertFalse(self.report_admin.has_change_permission(request))

    def test_has_delete_permission_superuser_only(self):
        """삭제 권한 테스트 (슈퍼유저만 가능)"""
        # 일반 사용자
        request = self.factory.get("/admin/reports/report/")
        request.user = self.user
        self.assertFalse(self.report_admin.has_delete_permission(request))

        # 슈퍼유저
        superuser = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123",
        )
        request.user = superuser
        self.assertTrue(self.report_admin.has_delete_permission(request))

    def test_fieldsets_configuration(self):
        """fieldsets 설정 테스트"""
        expected_fieldsets = (
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
        self.assertEqual(self.report_admin.fieldsets, expected_fieldsets)

    def test_inlines_configuration(self):
        """inlines 설정 테스트"""
        self.assertEqual(len(self.report_admin.inlines), 1)
        self.assertEqual(self.report_admin.inlines[0], GameReportInline)

    def test_search_by_username(self):
        """사용자명으로 검색 테스트"""
        request = self.factory.get("/admin/reports/report/", {"q": "testuser"})
        request.user = self.user

        queryset = self.report_admin.get_queryset(request)
        search_queryset = self.report_admin.get_search_results(request, queryset, "testuser")

        result_queryset = search_queryset[0]
        self.assertIn(self.report, result_queryset)

    def test_search_by_email(self):
        """이메일로 검색 테스트"""
        request = self.factory.get("/admin/reports/report/", {"q": "test@example.com"})
        request.user = self.user

        queryset = self.report_admin.get_queryset(request)
        search_queryset = self.report_admin.get_search_results(request, queryset, "test@example.com")

        result_queryset = search_queryset[0]
        self.assertIn(self.report, result_queryset)

    def test_search_by_child_name(self):
        """자녀 이름으로 검색 테스트"""
        request = self.factory.get("/admin/reports/report/", {"q": "Test Child"})
        request.user = self.user

        queryset = self.report_admin.get_queryset(request)
        search_queryset = self.report_admin.get_search_results(request, queryset, "Test Child")

        result_queryset = search_queryset[0]
        self.assertIn(self.report, result_queryset)


@pytest.mark.django_db
class GameReportInlineTests(TestCase):
    """GameReportInline 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.factory = RequestFactory()
        self.admin_site = AdminSite()
        self.inline = GameReportInline(Report, self.admin_site)

        # 사용자 생성
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="pass123",
        )

        # 자녀 생성
        self.child = Child.objects.create(
            parent=self.user,
            name="Test Child",
            birth_year=2020,
            gender="M",
        )

        # 게임 생성
        self.game = Game.objects.create(
            name="Test Game",
            code="TEST_GAME",
            max_round=10,
            is_active=True,
        )

        # 레포트 생성
        self.report = Report.objects.create(
            user=self.user,
            child=self.child,
        )

        # 게임 레포트 생성
        self.game_report = GameReport.objects.create(
            report=self.report,
            game=self.game,
        )

    def test_model_configuration(self):
        """모델 설정 테스트"""
        self.assertEqual(self.inline.model, GameReport)

    def test_extra_configuration(self):
        """extra 설정 테스트"""
        self.assertEqual(self.inline.extra, 0)

    def test_can_delete_configuration(self):
        """can_delete 설정 테스트"""
        self.assertFalse(self.inline.can_delete)

    def test_show_change_link_configuration(self):
        """show_change_link 설정 테스트"""
        self.assertTrue(self.inline.show_change_link)

    def test_fields_configuration(self):
        """fields 설정 테스트"""
        expected_fields = (
            "game",
            "last_reflected_session",
            "is_up_to_date_display",
            "view_details_link",
            "updated_at",
        )
        self.assertEqual(self.inline.fields, expected_fields)

    def test_readonly_fields_configuration(self):
        """readonly_fields 설정 테스트"""
        expected_fields = (
            "game",
            "last_reflected_session",
            "is_up_to_date_display",
            "view_details_link",
            "updated_at",
        )
        self.assertEqual(self.inline.readonly_fields, expected_fields)

    def test_is_up_to_date_display_with_pk(self):
        """is_up_to_date_display 메서드 테스트 (pk가 있는 경우)"""
        result = self.inline.is_up_to_date_display(self.game_report)

        # HTML이 포함되어 있는지 확인
        self.assertIn("<span", result)

    def test_is_up_to_date_display_without_pk(self):
        """is_up_to_date_display 메서드 테스트 (pk가 없는 경우)"""
        game_report_without_pk = GameReport(report=self.report, game=self.game)

        result = self.inline.is_up_to_date_display(game_report_without_pk)
        self.assertEqual(result, "-")

    def test_is_up_to_date_display_short_description(self):
        """is_up_to_date_display의 short_description 테스트"""
        self.assertEqual(self.inline.is_up_to_date_display.short_description, "최신 반영")

    def test_view_details_link_with_pk(self):
        """view_details_link 메서드 테스트 (pk가 있는 경우)"""
        result = self.inline.view_details_link(self.game_report)

        # 링크가 포함되어 있는지 확인
        self.assertIn("<a href=", result)
        self.assertIn("상세보기", result)
        self.assertIn(str(self.game_report.pk), result)

    def test_view_details_link_without_pk(self):
        """view_details_link 메서드 테스트 (pk가 없는 경우)"""
        game_report_without_pk = GameReport(report=self.report, game=self.game)

        result = self.inline.view_details_link(game_report_without_pk)
        self.assertEqual(result, "-")

    def test_view_details_link_short_description(self):
        """view_details_link의 short_description 테스트"""
        self.assertEqual(self.inline.view_details_link.short_description, "상세")

    def test_has_add_permission_false(self):
        """생성 권한 테스트 (불가능해야 함)"""
        request = self.factory.get("/admin/reports/report/")
        request.user = self.user

        self.assertFalse(self.inline.has_add_permission(request))
