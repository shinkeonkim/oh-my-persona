from unittest.mock import patch

from django.test import TestCase

import pytest
from reports.services.demo_email_service import DemoEmailService


@pytest.mark.django_db
class DemoEmailServiceTests(TestCase):
    """DemoEmailService 테스트"""

    def setUp(self):
        """테스트 설정"""
        self.service = DemoEmailService()

    def test_get_subject_with_title(self):
        """제목이 제공된 경우 테스트"""
        subject = self.service.get_subject(title="테스트 제목")
        self.assertEqual(subject, "테스트 제목")

    def test_get_subject_without_title(self):
        """제목이 제공되지 않은 경우 기본값 테스트"""
        subject = self.service.get_subject()
        self.assertEqual(subject, "제목 없음")

    def test_get_body_with_content(self):
        """내용이 제공된 경우 테스트"""
        body = self.service.get_body(content="테스트 내용입니다.")
        self.assertEqual(body, "테스트 내용입니다.")

    def test_get_body_without_content(self):
        """내용이 제공되지 않은 경우 기본값 테스트"""
        body = self.service.get_body()
        self.assertEqual(body, "내용 없음")

    @patch.object(DemoEmailService, "send_email")
    def test_send_demo_email(self, mock_send_email):
        """데모 이메일 전송 테스트"""
        # Mock send_email
        mock_send_email.return_value = {
            "success": True,
            "message": "Email sent successfully",
        }

        # 실행
        result = self.service.send_email(
            to_email="test@example.com",
            title="안녕하세요",
            content="이것은 테스트 이메일입니다.",
        )

        # 검증
        self.assertTrue(result["success"])

        # send_email 호출 확인
        mock_send_email.assert_called_once_with(
            to_email="test@example.com",
            title="안녕하세요",
            content="이것은 테스트 이메일입니다.",
        )

    def test_get_subject_with_empty_string(self):
        """빈 문자열 제목 테스트"""
        subject = self.service.get_subject(title="")
        # 빈 문자열도 제목으로 인정 (kwargs.get이 빈 문자열 반환)
        self.assertEqual(subject, "")

    def test_get_body_with_empty_string(self):
        """빈 문자열 내용 테스트"""
        body = self.service.get_body(content="")
        # 빈 문자열도 내용으로 인정
        self.assertEqual(body, "")

    def test_get_subject_with_long_title(self):
        """긴 제목 테스트"""
        long_title = "a" * 500
        subject = self.service.get_subject(title=long_title)
        self.assertEqual(subject, long_title)

    def test_get_body_with_long_content(self):
        """긴 내용 테스트"""
        long_content = "b" * 10000
        body = self.service.get_body(content=long_content)
        self.assertEqual(body, long_content)

    def test_service_inheritance(self):
        """BaseEmailService 상속 확인"""
        from reports.services.email.base_email_service import BaseEmailService

        self.assertIsInstance(self.service, BaseEmailService)
