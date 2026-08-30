from unittest.mock import Mock, patch

from django.contrib import messages
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.urls import reverse

import pytest

from users.admin.user_admin import UserAdmin
from users.models import BotToken

User = get_user_model()


@pytest.mark.django_db
class UserAdminTests(TestCase):
    """UserAdmin 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.factory = RequestFactory()
        self.admin_site = AdminSite()
        self.user_admin = UserAdmin(User, self.admin_site)

        # 관리자 사용자 생성
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123",
        )

        # 일반 사용자 생성
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

    def test_list_display_configuration(self):
        """list_display 설정 테스트"""
        expected_fields = (
            "email",
            "username",
            "is_active",
            "is_staff",
            "is_superuser",
        )
        self.assertEqual(self.user_admin.list_display, expected_fields)

    def test_list_filter_configuration(self):
        """list_filter 설정 테스트"""
        expected_filters = (
            "is_active",
            "is_staff",
            "is_superuser",
            "created_at",
        )
        self.assertEqual(self.user_admin.list_filter, expected_filters)

    def test_search_fields_configuration(self):
        """search_fields 설정 테스트"""
        expected_fields = (
            "email",
            "username",
        )
        self.assertEqual(self.user_admin.search_fields, expected_fields)

    def test_readonly_fields_configuration(self):
        """readonly_fields 설정 테스트"""
        expected_fields = (
            "is_active",
            "is_staff",
            "is_superuser",
            "created_at",
            "updated_at",
        )
        self.assertEqual(self.user_admin.readonly_fields, expected_fields)

    def test_ordering_configuration(self):
        """ordering 설정 테스트"""
        self.assertEqual(self.user_admin.ordering, ("-created_at",))

    def test_generate_bot_token_action_exists(self):
        """generate_bot_token 액션이 존재하는지 테스트"""
        self.assertIn("generate_bot_token", self.user_admin.actions)

    def test_generate_bot_token_single_user_success(self):
        """단일 사용자에 대한 BOT 토큰 생성 성공 테스트"""
        # 요청 생성
        request = self.factory.post("/admin/users/user/")
        request.user = self.admin_user
        request._messages = Mock()

        # 쿼리셋 생성
        queryset = User.objects.filter(id=self.user1.id)

        # 액션 실행
        self.user_admin.generate_bot_token(request, queryset)

        # BOT 토큰이 생성되었는지 확인
        bot_token = BotToken.objects.filter(user=self.user1).first()
        self.assertIsNotNone(bot_token)
        self.assertTrue(bot_token.token.startswith("X-BOT-TOKEN-"))

    def test_generate_bot_token_multiple_users_success(self):
        """여러 사용자에 대한 BOT 토큰 생성 성공 테스트"""
        # 요청 생성
        request = self.factory.post("/admin/users/user/")
        request.user = self.admin_user
        request._messages = Mock()

        # 쿼리셋 생성
        queryset = User.objects.filter(id__in=[self.user1.id, self.user2.id])

        # 액션 실행
        self.user_admin.generate_bot_token(request, queryset)

        # 두 사용자 모두에 대해 BOT 토큰이 생성되었는지 확인
        bot_token1 = BotToken.objects.filter(user=self.user1).first()
        bot_token2 = BotToken.objects.filter(user=self.user2).first()

        self.assertIsNotNone(bot_token1)
        self.assertIsNotNone(bot_token2)
        self.assertNotEqual(bot_token1.token, bot_token2.token)

    def test_generate_bot_token_shows_success_message(self):
        """BOT 토큰 생성 시 성공 메시지 표시 테스트"""
        # 요청 생성
        request = self.factory.post("/admin/users/user/")
        request.user = self.admin_user
        request._messages = Mock()

        # 쿼리셋 생성
        queryset = User.objects.filter(id=self.user1.id)

        # 액션 실행
        with patch.object(messages, "success") as mock_success:
            with patch.object(self.user_admin, "message_user") as mock_message_user:
                self.user_admin.generate_bot_token(request, queryset)

                # success 메시지가 호출되었는지 확인
                mock_success.assert_called_once()
                call_args = mock_success.call_args
                self.assertEqual(call_args[0][0], request)
                self.assertIn("user1", str(call_args[0][1]))
                self.assertIn("user1@example.com", str(call_args[0][1]))

                # message_user도 호출되었는지 확인
                mock_message_user.assert_called_once()
                message_call_args = mock_message_user.call_args[0]
                self.assertIn("1개의 BOT 토큰이 생성되었습니다", message_call_args[1])

    def test_generate_bot_token_error_handling(self):
        """BOT 토큰 생성 중 오류 발생 시 처리 테스트"""
        # 요청 생성
        request = self.factory.post("/admin/users/user/")
        request.user = self.admin_user
        request._messages = Mock()

        # 쿼리셋 생성
        queryset = User.objects.filter(id=self.user1.id)

        # create_for_report 메서드가 예외를 발생시키도록 설정
        with patch.object(BotToken, "create_for_report", side_effect=Exception("테스트 오류")):
            with patch.object(messages, "error") as mock_error:
                with patch.object(self.user_admin, "message_user") as mock_message_user:
                    self.user_admin.generate_bot_token(request, queryset)

                    # error 메시지가 호출되었는지 확인
                    mock_error.assert_called_once()
                    call_args = mock_error.call_args[0]
                    self.assertIn("user1", call_args[1])
                    self.assertIn("테스트 오류", call_args[1])

                    # error message_user도 호출되었는지 확인
                    mock_message_user.assert_called_once()
                    message_call_args = mock_message_user.call_args[0]
                    self.assertIn("1개의 BOT 토큰 생성에 실패했습니다", message_call_args[1])
                    self.assertEqual(message_call_args[2], messages.ERROR)

    def test_generate_bot_token_mixed_success_and_error(self):
        """일부 성공, 일부 실패 시 메시지 테스트"""
        # 요청 생성
        request = self.factory.post("/admin/users/user/")
        request.user = self.admin_user
        request._messages = Mock()

        # 쿼리셋 생성
        queryset = User.objects.filter(id__in=[self.user1.id, self.user2.id])

        # user2에 대해서만 예외 발생
        original_create = BotToken.create_for_report

        def side_effect(user):
            if user.id == self.user2.id:
                raise Exception("user2 오류")
            return original_create(user)

        with patch.object(BotToken, "create_for_report", side_effect=side_effect):
            with patch.object(self.user_admin, "message_user") as mock_message_user:
                self.user_admin.generate_bot_token(request, queryset)

                # message_user가 두 번 호출되었는지 확인 (success, error 각 1번)
                self.assertEqual(mock_message_user.call_count, 2)

                # 첫 번째 호출: 성공 메시지
                first_call = mock_message_user.call_args_list[0][0]
                self.assertIn("1개의 BOT 토큰이 생성되었습니다", first_call[1])
                self.assertEqual(first_call[2], messages.SUCCESS)

                # 두 번째 호출: 에러 메시지
                second_call = mock_message_user.call_args_list[1][0]
                self.assertIn("1개의 BOT 토큰 생성에 실패했습니다", second_call[1])
                self.assertEqual(second_call[2], messages.ERROR)

    def test_generate_bot_token_creates_admin_link(self):
        """BOT 토큰 생성 시 어드민 링크가 포함되는지 테스트"""
        # 요청 생성
        request = self.factory.post("/admin/users/user/")
        request.user = self.admin_user
        request._messages = Mock()

        # 쿼리셋 생성
        queryset = User.objects.filter(id=self.user1.id)

        # 액션 실행
        with patch.object(messages, "success") as mock_success:
            self.user_admin.generate_bot_token(request, queryset)

            # success 메시지에 어드민 링크가 포함되어 있는지 확인
            call_args = mock_success.call_args[0]
            message_html = str(call_args[1])

            # 토큰을 가져와서 링크 확인
            bot_token = BotToken.objects.filter(user=self.user1).first()
            expected_url = reverse("admin:users_bottoken_change", args=[bot_token.pk])

            self.assertIn(expected_url, message_html)
            self.assertIn("토큰 보기", message_html)

    def test_generate_bot_token_action_description(self):
        """generate_bot_token 액션의 description 테스트"""
        action = self.user_admin.generate_bot_token
        self.assertEqual(action.short_description, "선택한 사용자에 대한 BOT 토큰 생성")

    def test_fields_configuration(self):
        """fields 설정 테스트"""
        expected_fields = (
            "email",
            "username",
            "is_active",
            "is_staff",
            "is_superuser",
            "created_at",
            "updated_at",
        )
        self.assertEqual(self.user_admin.fields, expected_fields)

    def test_generate_bot_token_no_duplicate_tokens(self):
        """BOT 토큰 생성 시 중복 토큰이 생성되지 않는지 테스트"""
        # 요청 생성
        request = self.factory.post("/admin/users/user/")
        request.user = self.admin_user
        request._messages = Mock()

        # 쿼리셋 생성
        queryset = User.objects.filter(id=self.user1.id)

        # 첫 번째 토큰 생성
        self.user_admin.generate_bot_token(request, queryset)
        BotToken.objects.filter(user=self.user1).first().token

        # 두 번째 토큰 생성
        self.user_admin.generate_bot_token(request, queryset)

        # 토큰 개수 확인 (사용자당 여러 토큰 생성 가능)
        tokens = BotToken.objects.filter(user=self.user1)
        self.assertEqual(tokens.count(), 2)

        # 토큰들이 서로 다른지 확인
        token_values = [t.token for t in tokens]
        self.assertEqual(len(token_values), len(set(token_values)))
