from unittest.mock import patch

from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

import pytest

from common.admin.utils import render_two_line_info
from users.admin.bot_token_admin import BotTokenAdmin
from users.models import BotToken

User = get_user_model()


@pytest.mark.django_db
class BotTokenAdminTests(TestCase):
    """BotTokenAdmin 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.factory = RequestFactory()
        self.admin_site = AdminSite()
        self.bot_token_admin = BotTokenAdmin(BotToken, self.admin_site)

        # 사용자 생성
        self.user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="pass123",
        )
        self.user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="pass123",
        )

        # BOT 토큰 생성
        self.token1 = BotToken.objects.create(
            user=self.user1,
            token="X-BOT-TOKEN-test1234567890",
        )
        self.token2 = BotToken.objects.create(
            user=self.user2,
            token="X-BOT-TOKEN-test0987654321",
        )

    def test_list_display_configuration(self):
        """list_display 설정 테스트"""
        expected_fields = (
            "id",
            "user_id_display",
            "created_at",
        )
        self.assertEqual(self.bot_token_admin.list_display, expected_fields)

    def test_list_filter_configuration(self):
        """list_filter 설정 테스트"""
        expected_filters = ("created_at",)
        self.assertEqual(self.bot_token_admin.list_filter, expected_filters)

    def test_search_fields_configuration(self):
        """search_fields 설정 테스트"""
        expected_fields = (
            "user__username",
            "user__email",
            "token",
        )
        self.assertEqual(self.bot_token_admin.search_fields, expected_fields)

    def test_ordering_configuration(self):
        """ordering 설정 테스트"""
        self.assertEqual(self.bot_token_admin.ordering, ("-created_at",))

    def test_date_hierarchy_configuration(self):
        """date_hierarchy 설정 테스트"""
        self.assertEqual(self.bot_token_admin.date_hierarchy, "created_at")

    def test_readonly_fields_configuration(self):
        """readonly_fields 설정 테스트"""
        expected_fields = ("created_at", "updated_at")
        self.assertEqual(self.bot_token_admin.readonly_fields, expected_fields)

    def test_autocomplete_fields_configuration(self):
        """autocomplete_fields 설정 테스트"""
        expected_fields = ("user",)
        self.assertEqual(self.bot_token_admin.autocomplete_fields, expected_fields)

    def test_list_per_page_configuration(self):
        """list_per_page 설정 테스트"""
        self.assertEqual(self.bot_token_admin.list_per_page, 25)

    def test_show_full_result_count_configuration(self):
        """show_full_result_count 설정 테스트"""
        self.assertTrue(self.bot_token_admin.show_full_result_count)

    def test_user_id_display_with_user(self):
        """user_id_display 메서드 테스트 (사용자가 있는 경우)"""
        result = self.bot_token_admin.user_id_display(self.token1)

        # render_two_line_info가 호출되었는지 확인
        expected = render_two_line_info(f"#{self.user1.id}", self.user1.username)
        self.assertEqual(result, expected)

        # HTML 형식 확인
        self.assertIn(str(self.user1.id), result)
        self.assertIn(self.user1.username, result)
        self.assertIn("<strong>", result)
        self.assertIn("<small>", result)

    def test_user_id_display_without_user(self):
        """user_id_display 메서드 테스트 (사용자가 없는 경우)"""
        # Mock 객체를 사용하여 user가 없는 상황 시뮬레이션
        from unittest.mock import Mock

        token_without_user = Mock(spec=BotToken)
        token_without_user.user = None

        result = self.bot_token_admin.user_id_display(token_without_user)
        self.assertEqual(result, "-")

    def test_user_id_display_short_description(self):
        """user_id_display의 short_description 테스트"""
        self.assertEqual(self.bot_token_admin.user_id_display.short_description, "사용자")

    def test_user_id_display_admin_order_field(self):
        """user_id_display의 admin_order_field 테스트"""
        self.assertEqual(self.bot_token_admin.user_id_display.admin_order_field, "user__id")

    def test_get_queryset_optimization(self):
        """get_queryset 메서드의 select_related 최적화 테스트"""
        request = self.factory.get("/admin/users/bottoken/")
        request.user = self.user1

        with self.assertNumQueries(1):  # user가 select_related로 최적화되어야 함
            queryset = self.bot_token_admin.get_queryset(request)
            list(queryset)  # 쿼리셋을 평가

        # select_related가 적용되었는지 확인
        queryset = self.bot_token_admin.get_queryset(request)
        self.assertIn("user", queryset.query.select_related)

    def test_get_queryset_includes_all_tokens(self):
        """get_queryset가 모든 토큰을 포함하는지 테스트"""
        request = self.factory.get("/admin/users/bottoken/")
        request.user = self.user1

        queryset = self.bot_token_admin.get_queryset(request)

        self.assertEqual(queryset.count(), 2)
        self.assertIn(self.token1, queryset)
        self.assertIn(self.token2, queryset)

    def test_fieldsets_configuration(self):
        """fieldsets 설정 테스트"""
        expected_fieldsets = (
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
        self.assertEqual(self.bot_token_admin.fieldsets, expected_fieldsets)

    def test_search_by_username(self):
        """사용자명으로 검색 테스트"""
        request = self.factory.get("/admin/users/bottoken/", {"q": "user1"})
        request.user = self.user1

        queryset = self.bot_token_admin.get_queryset(request)
        search_queryset = self.bot_token_admin.get_search_results(request, queryset, "user1")

        result_queryset = search_queryset[0]

        # user1의 토큰이 조회되어야 함
        self.assertIn(self.token1, result_queryset)

    def test_search_by_email(self):
        """이메일로 검색 테스트"""
        request = self.factory.get("/admin/users/bottoken/", {"q": "user2@example.com"})
        request.user = self.user2

        queryset = self.bot_token_admin.get_queryset(request)
        search_queryset = self.bot_token_admin.get_search_results(request, queryset, "user2@example.com")

        result_queryset = search_queryset[0]

        # user2의 토큰이 조회되어야 함
        self.assertIn(self.token2, result_queryset)

    def test_search_by_token(self):
        """토큰으로 검색 테스트"""
        request = self.factory.get("/admin/users/bottoken/", {"q": "test1234567890"})
        request.user = self.user1

        queryset = self.bot_token_admin.get_queryset(request)
        search_queryset = self.bot_token_admin.get_search_results(request, queryset, "test1234567890")

        result_queryset = search_queryset[0]

        # 해당 토큰이 조회되어야 함
        self.assertIn(self.token1, result_queryset)

    def test_ordering_by_created_at_descending(self):
        """created_at 내림차순 정렬 테스트"""
        request = self.factory.get("/admin/users/bottoken/")
        request.user = self.user1

        queryset = self.bot_token_admin.get_queryset(request)

        # 쿼리셋의 ordering 확인
        ordering = queryset.query.order_by
        self.assertIn("-created_at", ordering)

    def test_user_id_display_format(self):
        """user_id_display의 포맷 테스트"""
        result = self.bot_token_admin.user_id_display(self.token1)

        # HTML 태그가 포함되어 있는지 확인
        self.assertIn("<strong>", result)
        self.assertIn("</strong>", result)
        self.assertIn("<br/>", result)
        self.assertIn("<small>", result)
        self.assertIn("</small>", result)

        # 사용자 ID와 이름이 올바르게 표시되는지 확인
        self.assertIn(f"#{self.user1.id}", result)
        self.assertIn(self.user1.username, result)

    def test_user_id_display_uses_render_two_line_info(self):
        """user_id_display가 render_two_line_info를 사용하는지 테스트"""
        with patch("users.admin.bot_token_admin.render_two_line_info") as mock_render:
            mock_render.return_value = "mocked result"

            result = self.bot_token_admin.user_id_display(self.token1)

            # render_two_line_info가 올바른 인자로 호출되었는지 확인
            mock_render.assert_called_once_with(f"#{self.user1.id}", self.user1.username)
            self.assertEqual(result, "mocked result")

    def test_fieldsets_system_info_collapsed(self):
        """시스템 정보 fieldset이 collapse 클래스를 가지는지 테스트"""
        fieldsets = self.bot_token_admin.fieldsets

        # 두 번째 fieldset (시스템 정보)
        system_info_fieldset = fieldsets[1]
        self.assertEqual(system_info_fieldset[0], "시스템 정보")
        self.assertIn("collapse", system_info_fieldset[1]["classes"])

    def test_model_str_representation(self):
        """BotToken 모델의 문자열 표현 테스트"""
        token_str = str(self.token1)
        self.assertIn(self.user1.email, token_str)
        self.assertIn(self.token1.token, token_str)
        self.assertIn("BOT Token", token_str)
