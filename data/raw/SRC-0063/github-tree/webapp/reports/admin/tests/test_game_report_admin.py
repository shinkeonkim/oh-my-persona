from unittest.mock import Mock

from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

import pytest
from games.models import Game, GameSession
from reports.admin.game_report_admin import GameReportAdmin, GameReportAdviceInline
from reports.models import GameReport, GameReportAdvice, Report

from users.models import Child

User = get_user_model()


@pytest.mark.django_db
class GameReportAdminTests(TestCase):
    """GameReportAdmin 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.factory = RequestFactory()
        self.admin_site = AdminSite()
        self.game_report_admin = GameReportAdmin(GameReport, self.admin_site)

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

        # 게임 세션 생성
        self.session = GameSession.objects.create(
            parent=self.user,
            child=self.child,
            game=self.game,
        )

        # 게임 레포트 생성
        self.game_report = GameReport.objects.create(
            report=self.report,
            game=self.game,
            last_reflected_session=self.session,
        )

    def test_list_display_configuration(self):
        """list_display 설정 테스트"""
        expected_fields = (
            "id",
            "report_info",
            "game_info",
            "is_up_to_date_display",
            "advice_count_display",
            "updated_at",
        )
        self.assertEqual(self.game_report_admin.list_display, expected_fields)

    def test_list_filter_configuration(self):
        """list_filter 설정 테스트"""
        expected_filters = (
            "game",
            "updated_at",
        )
        self.assertEqual(self.game_report_admin.list_filter, expected_filters)

    def test_search_fields_configuration(self):
        """search_fields 설정 테스트"""
        expected_fields = (
            "report__user__username",
            "report__user__email",
            "report__child__name",
            "game__name",
        )
        self.assertEqual(self.game_report_admin.search_fields, expected_fields)

    def test_ordering_configuration(self):
        """ordering 설정 테스트"""
        self.assertEqual(self.game_report_admin.ordering, ("-updated_at",))

    def test_date_hierarchy_configuration(self):
        """date_hierarchy 설정 테스트"""
        self.assertEqual(self.game_report_admin.date_hierarchy, "updated_at")

    def test_readonly_fields_configuration(self):
        """readonly_fields 설정 테스트"""
        expected_fields = (
            "report",
            "game",
            "last_reflected_session",
            "meta",
            "created_at",
            "updated_at",
        )
        self.assertEqual(self.game_report_admin.readonly_fields, expected_fields)

    def test_autocomplete_fields_configuration(self):
        """autocomplete_fields 설정 테스트"""
        expected_fields = ("report", "game", "last_reflected_session")
        self.assertEqual(self.game_report_admin.autocomplete_fields, expected_fields)

    def test_list_per_page_configuration(self):
        """list_per_page 설정 테스트"""
        self.assertEqual(self.game_report_admin.list_per_page, 25)

    def test_show_full_result_count_configuration(self):
        """show_full_result_count 설정 테스트"""
        self.assertTrue(self.game_report_admin.show_full_result_count)

    def test_report_info_display_with_report(self):
        """report_info 메서드 테스트 (레포트가 있는 경우)"""
        result = self.game_report_admin.report_info(self.game_report)

        # HTML 형식 확인
        self.assertIn(self.user.username, result)
        self.assertIn(self.child.name, result)
        self.assertIn(f"Report #{self.report.id}", result)
        self.assertIn("<strong>", result)
        self.assertIn("<small>", result)

    def test_report_info_display_without_report(self):
        """report_info 메서드 테스트 (레포트가 없는 경우)"""
        mock_game_report = Mock(spec=GameReport)
        mock_game_report.report = None

        result = self.game_report_admin.report_info(mock_game_report)
        self.assertEqual(result, "-")

    def test_report_info_short_description(self):
        """report_info의 short_description 테스트"""
        self.assertEqual(self.game_report_admin.report_info.short_description, "레포트")

    def test_report_info_admin_order_field(self):
        """report_info의 admin_order_field 테스트"""
        self.assertEqual(self.game_report_admin.report_info.admin_order_field, "report__user__username")

    def test_game_info_display_with_game(self):
        """game_info 메서드 테스트 (게임이 있는 경우)"""
        result = self.game_report_admin.game_info(self.game_report)

        # HTML 형식 확인
        self.assertIn(self.game.name, result)
        self.assertIn("<strong>", result)

    def test_game_info_display_without_game(self):
        """game_info 메서드 테스트 (게임이 없는 경우)"""
        mock_game_report = Mock(spec=GameReport)
        mock_game_report.game = None

        result = self.game_report_admin.game_info(mock_game_report)
        self.assertEqual(result, "-")

    def test_game_info_short_description(self):
        """game_info의 short_description 테스트"""
        self.assertEqual(self.game_report_admin.game_info.short_description, "게임")

    def test_game_info_admin_order_field(self):
        """game_info의 admin_order_field 테스트"""
        self.assertEqual(self.game_report_admin.game_info.admin_order_field, "game__name")

    def test_is_up_to_date_display(self):
        """is_up_to_date_display 메서드 테스트"""
        result = self.game_report_admin.is_up_to_date_display(self.game_report)

        # HTML이 포함되어 있는지 확인
        self.assertIn("<span", result)

    def test_is_up_to_date_display_short_description(self):
        """is_up_to_date_display의 short_description 테스트"""
        self.assertEqual(self.game_report_admin.is_up_to_date_display.short_description, "최신 반영")

    def test_advice_count_display(self):
        """advice_count_display 메서드 테스트"""
        # 조언 생성
        GameReportAdvice.objects.create(
            game_report=self.game_report,
            game=self.game,
            title="Test Advice",
            description="Test Description",
        )

        result = self.game_report_admin.advice_count_display(self.game_report)

        # 카운트가 포함되어 있는지 확인
        self.assertIn("1", result)

    def test_advice_count_display_short_description(self):
        """advice_count_display의 short_description 테스트"""
        self.assertEqual(self.game_report_admin.advice_count_display.short_description, "조언 수")

    def test_get_queryset_optimization(self):
        """get_queryset 메서드의 최적화 테스트"""
        request = self.factory.get("/admin/reports/gamereport/")
        request.user = self.user

        queryset = self.game_report_admin.get_queryset(request)

        # select_related 확인 (중첩 구조)
        select_related_dict = queryset.query.select_related
        self.assertIn("report", select_related_dict)
        self.assertIn("user", select_related_dict["report"])
        self.assertIn("child", select_related_dict["report"])
        self.assertIn("game", select_related_dict)
        self.assertIn("last_reflected_session", select_related_dict)

    def test_has_add_permission_false(self):
        """생성 권한 테스트 (불가능해야 함)"""
        request = self.factory.get("/admin/reports/gamereport/")
        request.user = self.user

        self.assertFalse(self.game_report_admin.has_add_permission(request))

    def test_has_change_permission_false(self):
        """수정 권한 테스트 (가능해야 함)"""
        request = self.factory.get("/admin/reports/gamereport/")
        request.user = self.user

        self.assertTrue(self.game_report_admin.has_change_permission(request))

    def test_has_delete_permission_superuser_only(self):
        """삭제 권한 테스트 (슈퍼유저만 가능)"""
        # 일반 사용자
        request = self.factory.get("/admin/reports/gamereport/")
        request.user = self.user
        self.assertFalse(self.game_report_admin.has_delete_permission(request))

        # 슈퍼유저
        superuser = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123",
        )
        request.user = superuser
        self.assertTrue(self.game_report_admin.has_delete_permission(request))

    def test_fieldsets_configuration(self):
        """fieldsets 설정 테스트"""
        expected_fieldsets = (
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
        self.assertEqual(self.game_report_admin.fieldsets, expected_fieldsets)

    def test_inlines_configuration(self):
        """inlines 설정 테스트"""
        self.assertEqual(len(self.game_report_admin.inlines), 1)
        self.assertEqual(self.game_report_admin.inlines[0], GameReportAdviceInline)

    def test_search_by_username(self):
        """사용자명으로 검색 테스트"""
        request = self.factory.get("/admin/reports/gamereport/", {"q": "testuser"})
        request.user = self.user

        queryset = self.game_report_admin.get_queryset(request)
        search_queryset = self.game_report_admin.get_search_results(request, queryset, "testuser")

        result_queryset = search_queryset[0]
        self.assertIn(self.game_report, result_queryset)

    def test_search_by_email(self):
        """이메일로 검색 테스트"""
        request = self.factory.get("/admin/reports/gamereport/", {"q": "test@example.com"})
        request.user = self.user

        queryset = self.game_report_admin.get_queryset(request)
        search_queryset = self.game_report_admin.get_search_results(request, queryset, "test@example.com")

        result_queryset = search_queryset[0]
        self.assertIn(self.game_report, result_queryset)

    def test_search_by_child_name(self):
        """자녀 이름으로 검색 테스트"""
        request = self.factory.get("/admin/reports/gamereport/", {"q": "Test Child"})
        request.user = self.user

        queryset = self.game_report_admin.get_queryset(request)
        search_queryset = self.game_report_admin.get_search_results(request, queryset, "Test Child")

        result_queryset = search_queryset[0]
        self.assertIn(self.game_report, result_queryset)

    def test_search_by_game_name(self):
        """게임 이름으로 검색 테스트"""
        request = self.factory.get("/admin/reports/gamereport/", {"q": "Test Game"})
        request.user = self.user

        queryset = self.game_report_admin.get_queryset(request)
        search_queryset = self.game_report_admin.get_search_results(request, queryset, "Test Game")

        result_queryset = search_queryset[0]
        self.assertIn(self.game_report, result_queryset)


@pytest.mark.django_db
class GameReportAdviceInlineTests(TestCase):
    """GameReportAdviceInline 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.factory = RequestFactory()
        self.admin_site = AdminSite()
        self.inline = GameReportAdviceInline(GameReport, self.admin_site)

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

        # 게임 레포트 조언 생성
        self.advice = GameReportAdvice.objects.create(
            game_report=self.game_report,
            game=self.game,
            title="Test Advice",
            description="Test Description",
        )

    def test_model_configuration(self):
        """모델 설정 테스트"""
        self.assertEqual(self.inline.model, GameReportAdvice)

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
            "title",
            "description",
            "error_message",
            "created_at",
        )
        self.assertEqual(self.inline.fields, expected_fields)

    def test_readonly_fields_configuration(self):
        """readonly_fields 설정 테스트"""
        expected_fields = (
            "game",
            "error_message",
            "created_at",
        )
        self.assertEqual(self.inline.readonly_fields, expected_fields)

    def test_has_add_permission_false(self):
        """생성 권한 테스트 (불가능해야 함)"""
        request = self.factory.get("/admin/reports/gamereport/")
        request.user = self.user

        self.assertFalse(self.inline.has_add_permission(request))
