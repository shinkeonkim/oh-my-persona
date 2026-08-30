from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

import pytest
from reports.models import ReportPin
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
class SetReportPinAPIViewTests(TestCase):
    """SetReportPinAPIView 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com",
        )
        self.url = "/api/v1/reports/set-report-pin/"

    def test_set_report_pin_creates_new(self):
        """새 레포트 PIN 생성 테스트"""
        self.client.force_authenticate(user=self.user)

        data = {"pin": "1234"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_success"])

        # ReportPin이 생성되었는지 확인
        report_pin = ReportPin.objects.get(user=self.user)
        self.assertIsNotNone(report_pin)
        self.assertIsNotNone(report_pin.pin_hash)
        self.assertIsNotNone(report_pin.enabled_at)

        # PIN이 올바르게 저장되었는지 검증
        self.assertTrue(report_pin.verify_pin("1234"))

    def test_set_report_pin_updates_existing(self):
        """기존 레포트 PIN 업데이트 테스트"""
        # 기존 PIN 생성
        report_pin = ReportPin.objects.create(
            user=self.user,
            pin_hash="old_hash",
            enabled_at=timezone.now(),
        )
        old_id = report_pin.id

        self.client.force_authenticate(user=self.user)

        data = {"pin": "5678"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_success"])

        # 동일한 객체가 업데이트되었는지 확인
        report_pin.refresh_from_db()
        self.assertEqual(report_pin.id, old_id)

        # 새 PIN으로 검증
        self.assertTrue(report_pin.verify_pin("5678"))
        self.assertFalse(report_pin.verify_pin("1234"))

    def test_set_report_pin_requires_authentication(self):
        """인증 없이 요청 시 실패 테스트"""
        data = {"pin": "1234"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_set_report_pin_validates_min_length(self):
        """PIN 최소 길이 검증 테스트"""
        self.client.force_authenticate(user=self.user)

        data = {"pin": "123"}  # 3자리 (최소 4자리 필요)
        response = self.client.post(self.url, data, format="json")

        # DRF의 validation error는 422를 반환
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY])

    def test_set_report_pin_validates_max_length(self):
        """PIN 최대 길이 검증 테스트"""
        self.client.force_authenticate(user=self.user)

        data = {"pin": "1234567"}  # 7자리 (최대 6자리)
        response = self.client.post(self.url, data, format="json")

        # DRF의 validation error는 422를 반환
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY])

    def test_set_report_pin_requires_pin_field(self):
        """PIN 필드 필수 검증 테스트"""
        self.client.force_authenticate(user=self.user)

        data = {}  # PIN 없음
        response = self.client.post(self.url, data, format="json")

        # DRF의 validation error는 422를 반환
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY])

    def test_set_report_pin_valid_lengths(self):
        """유효한 PIN 길이 테스트 (4-6자리)"""
        self.client.force_authenticate(user=self.user)

        # 4자리
        response = self.client.post(self.url, {"pin": "1234"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 5자리
        response = self.client.post(self.url, {"pin": "12345"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 6자리
        response = self.client.post(self.url, {"pin": "123456"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_set_report_pin_updates_enabled_at(self):
        """PIN 업데이트 시 enabled_at 갱신 테스트"""
        # 기존 PIN 생성
        old_time = timezone.now() - timezone.timedelta(days=1)
        report_pin = ReportPin.objects.create(
            user=self.user,
            pin_hash="old_hash",
            enabled_at=old_time,
        )

        self.client.force_authenticate(user=self.user)

        data = {"pin": "9999"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        report_pin.refresh_from_db()
        # enabled_at이 업데이트되었는지 확인
        self.assertGreater(report_pin.enabled_at, old_time)

    def test_set_report_pin_response_structure(self):
        """응답 구조 검증 테스트"""
        self.client.force_authenticate(user=self.user)

        data = {"pin": "1234"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("is_success", response.data)
        self.assertIn("message", response.data)
        self.assertTrue(response.data["is_success"])
        self.assertEqual(response.data["message"], "Report pin set successfully.")

    def test_set_report_pin_different_users(self):
        """서로 다른 사용자의 PIN 독립성 테스트"""
        user2 = User.objects.create_user(
            username="testuser2",
            password="testpass123",
            email="test2@example.com",
        )

        # 첫 번째 사용자 PIN 설정
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {"pin": "1111"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 두 번째 사용자 PIN 설정
        self.client.force_authenticate(user=user2)
        response = self.client.post(self.url, {"pin": "2222"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 각 사용자의 PIN이 독립적으로 저장되었는지 확인
        pin1 = ReportPin.objects.get(user=self.user)
        pin2 = ReportPin.objects.get(user=user2)

        self.assertTrue(pin1.verify_pin("1111"))
        self.assertFalse(pin1.verify_pin("2222"))

        self.assertTrue(pin2.verify_pin("2222"))
        self.assertFalse(pin2.verify_pin("1111"))
