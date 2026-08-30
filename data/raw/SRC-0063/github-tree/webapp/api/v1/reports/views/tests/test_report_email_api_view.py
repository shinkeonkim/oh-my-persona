from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from users.models import BotToken, Child

User = get_user_model()


@pytest.mark.django_db
class ReportEmailAPIViewTests(TestCase):
    """ReportEmailAPIView 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com",
        )
        self.child = Child.objects.create(
            parent=self.user,
            name="Test Child",
            birth_year=2020,
            gender="M",
        )
        self.url = "/api/v1/reports/email/"

    @patch("api.v1.reports.views.report_email_api_view.send_report_email_task.delay")
    def test_send_report_email_success(self, mock_task):
        """레포트 이메일 전송 성공 테스트"""
        self.client.force_authenticate(user=self.user)

        data = {"email": "recipient@example.com"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)

        # BOT 토큰이 생성되었는지 확인
        bot_token = BotToken.objects.filter(user=self.user).first()
        self.assertIsNotNone(bot_token)

        # Celery task가 호출되었는지 확인
        mock_task.assert_called_once()
        call_kwargs = mock_task.call_args[1]
        self.assertEqual(call_kwargs["to_email"], "recipient@example.com")
        self.assertIn("BOT_TOKEN=", call_kwargs["site_url"])

    @patch("api.v1.reports.views.report_email_api_view.send_report_email_task.delay")
    def test_send_report_email_uses_user_email_if_not_provided(self, mock_task):
        """이메일이 제공되지 않으면 사용자 이메일 사용 테스트"""
        self.client.force_authenticate(user=self.user)

        data = {}  # email 없음
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 사용자 이메일로 task가 호출되었는지 확인
        mock_task.assert_called_once()
        call_kwargs = mock_task.call_args[1]
        self.assertEqual(call_kwargs["to_email"], self.user.email)

    @patch("api.v1.reports.views.report_email_api_view.send_report_email_task.delay")
    def test_send_report_email_no_email_error(self, mock_task):
        """이메일이 없고 사용자 이메일도 없을 때 에러 테스트"""
        # 이메일 없는 사용자
        user_no_email = User.objects.create_user(
            username="noemail",
            password="testpass123",
            email="",
        )
        self.client.force_authenticate(user=user_no_email)

        data = {}  # email 없음
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        mock_task.assert_not_called()

    def test_send_report_email_requires_authentication(self):
        """인증 없이 요청 시 실패 테스트"""
        data = {"email": "test@example.com"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("api.v1.reports.views.report_email_api_view.send_report_email_task.delay")
    def test_send_report_email_creates_bot_token(self, mock_task):
        """BOT 토큰 생성 테스트"""
        self.client.force_authenticate(user=self.user)

        initial_token_count = BotToken.objects.count()

        data = {"email": "test@example.com"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # BOT 토큰이 생성되었는지 확인
        self.assertEqual(BotToken.objects.count(), initial_token_count + 1)

        # 토큰이 올바른 사용자에게 생성되었는지 확인
        bot_token = BotToken.objects.filter(user=self.user).latest("created_at")
        self.assertEqual(bot_token.user, self.user)

    @patch("api.v1.reports.views.report_email_api_view.send_report_email_task.delay")
    def test_send_report_email_includes_bot_token_in_url(self, mock_task):
        """site_url에 BOT 토큰이 포함되는지 테스트"""
        self.client.force_authenticate(user=self.user)

        data = {"email": "test@example.com"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # site_url에 BOT_TOKEN 파라미터가 포함되었는지 확인
        call_kwargs = mock_task.call_args[1]
        self.assertIn("BOT_TOKEN=", call_kwargs["site_url"])

        # 생성된 토큰이 URL에 포함되어 있는지 확인
        bot_token = BotToken.objects.filter(user=self.user).latest("created_at")
        self.assertIn(bot_token.token, call_kwargs["site_url"])

    @patch("api.v1.reports.views.report_email_api_view.send_report_email_task.delay")
    def test_send_report_email_validates_email_format(self, mock_task):
        """이메일 형식 검증 테스트"""
        self.client.force_authenticate(user=self.user)

        # 잘못된 이메일 형식
        data = {"email": "invalid-email"}
        response = self.client.post(self.url, data, format="json")

        self.assertIn(
            response.status_code,
            [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY],
        )
        mock_task.assert_not_called()

    @patch("api.v1.reports.views.report_email_api_view.send_report_email_task.delay")
    def test_send_report_email_multiple_calls(self, mock_task):
        """여러 번 호출 시 각각 새로운 BOT 토큰 생성 테스트"""
        self.client.force_authenticate(user=self.user)

        data = {"email": "test@example.com"}

        # 첫 번째 호출
        response1 = self.client.post(self.url, data, format="json")
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        token1 = BotToken.objects.filter(user=self.user).latest("created_at").token

        # 두 번째 호출
        response2 = self.client.post(self.url, data, format="json")
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        token2 = BotToken.objects.filter(user=self.user).latest("created_at").token

        # 각각 다른 토큰이 생성되었는지 확인
        self.assertNotEqual(token1, token2)
        self.assertEqual(mock_task.call_count, 2)

    @patch("api.v1.reports.views.report_email_api_view.send_report_email_task.delay")
    def test_send_report_email_task_called_with_correct_params(self, mock_task):
        """Celery task가 올바른 파라미터로 호출되는지 테스트"""
        self.client.force_authenticate(user=self.user)

        data = {"email": "specific@example.com"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # task가 한 번 호출되었는지 확인
        mock_task.assert_called_once()

        # 호출 파라미터 확인
        call_kwargs = mock_task.call_args[1]
        self.assertEqual(call_kwargs["to_email"], "specific@example.com")
        self.assertIn("site_url", call_kwargs)
        self.assertTrue(call_kwargs["site_url"].startswith("http"))

    def test_send_report_email_inactive_user(self):
        """비활성화된 사용자 요청 시 실패 테스트"""
        inactive_user = User.objects.create_user(
            username="inactive",
            password="testpass123",
            email="inactive@example.com",
            is_active=False,
        )
        self.client.force_authenticate(user=inactive_user)

        data = {"email": "test@example.com"}
        response = self.client.post(self.url, data, format="json")

        # ActiveUserPermission에 의해 거부되어야 함
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch("api.v1.reports.views.report_email_api_view.send_report_email_task.delay")
    def test_send_report_email_response_message(self, mock_task):
        """응답 메시지 확인 테스트"""
        self.client.force_authenticate(user=self.user)

        data = {"email": "test@example.com"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "레포트 이메일 전송이 시작되었습니다.")

    @patch("api.v1.reports.views.report_email_api_view.send_report_email_task.delay")
    def test_send_report_email_with_empty_email_string(self, mock_task):
        """빈 이메일 문자열 제공 시 검증 실패 테스트"""
        self.client.force_authenticate(user=self.user)

        data = {"email": ""}  # 빈 문자열
        response = self.client.post(self.url, data, format="json")

        # 빈 문자열은 유효하지 않은 이메일 형식으로 간주됨
        self.assertIn(
            response.status_code,
            [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY],
        )
        mock_task.assert_not_called()
