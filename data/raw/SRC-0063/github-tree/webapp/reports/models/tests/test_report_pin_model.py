from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

import pytest
from reports.models import ReportPin

User = get_user_model()


@pytest.mark.django_db
class ReportPinModelTests(TestCase):
    """ReportPin 모델 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
        )

    def test_create_report_pin(self):
        """레포트 PIN 생성 테스트"""
        pin_hash = "test_hash_value"
        report_pin = ReportPin.objects.create(
            user=self.user,
            pin_hash=pin_hash,
        )

        self.assertEqual(report_pin.user, self.user)
        self.assertEqual(report_pin.pin_hash, pin_hash)
        self.assertIsNone(report_pin.enabled_at)

    def test_one_to_one_relationship(self):
        """사용자당 하나의 PIN만 가질 수 있는지 테스트"""
        ReportPin.objects.create(
            user=self.user,
            pin_hash="hash1",
        )

        # 같은 사용자에게 두 번째 PIN 생성 시도
        from django.db import IntegrityError

        with self.assertRaises(IntegrityError):
            ReportPin.objects.create(
                user=self.user,
                pin_hash="hash2",
            )

    def test_get_pin_hash(self):
        """PIN 해시 생성 테스트"""
        report_pin = ReportPin.objects.create(
            user=self.user,
            pin_hash="temp_hash",
        )

        pin = "1234"
        pin_hash = report_pin.get_pin_hash(pin)

        self.assertIsInstance(pin_hash, str)
        self.assertEqual(len(pin_hash), 64)  # SHA256 해시는 64자

        # 같은 PIN은 같은 해시를 생성해야 함
        pin_hash2 = report_pin.get_pin_hash(pin)
        self.assertEqual(pin_hash, pin_hash2)

    def test_get_pin_hash_different_pins(self):
        """다른 PIN은 다른 해시를 생성하는지 테스트"""
        report_pin = ReportPin.objects.create(
            user=self.user,
            pin_hash="temp_hash",
        )

        hash1 = report_pin.get_pin_hash("1234")
        hash2 = report_pin.get_pin_hash("5678")

        self.assertNotEqual(hash1, hash2)

    def test_get_pin_hash_without_user_id(self):
        """user_id가 없을 때 PIN 해시 생성 시도 테스트"""
        report_pin = ReportPin(pin_hash="temp_hash")
        # user_id가 설정되지 않음

        with self.assertRaises(ValueError) as context:
            report_pin.get_pin_hash("1234")

        self.assertIn("user_id is required", str(context.exception))

    def test_verify_pin_correct(self):
        """올바른 PIN 검증 테스트"""
        pin = "1234"
        report_pin = ReportPin.objects.create(
            user=self.user,
            pin_hash="temp_hash",
        )

        # 실제 해시로 업데이트
        correct_hash = report_pin.get_pin_hash(pin)
        report_pin.pin_hash = correct_hash
        report_pin.save()

        # 검증
        self.assertTrue(report_pin.verify_pin(pin))

    def test_verify_pin_incorrect(self):
        """잘못된 PIN 검증 테스트"""
        correct_pin = "1234"
        wrong_pin = "5678"

        report_pin = ReportPin.objects.create(
            user=self.user,
            pin_hash="temp_hash",
        )

        # 올바른 PIN의 해시 설정
        correct_hash = report_pin.get_pin_hash(correct_pin)
        report_pin.pin_hash = correct_hash
        report_pin.save()

        # 잘못된 PIN으로 검증 시도
        self.assertFalse(report_pin.verify_pin(wrong_pin))

    def test_verify_pin_without_hash(self):
        """PIN 해시가 설정되지 않았을 때 검증 테스트"""
        report_pin = ReportPin.objects.create(
            user=self.user,
            pin_hash="",  # 빈 해시
        )

        self.assertFalse(report_pin.verify_pin("1234"))

    def test_verify_pin_without_user_id(self):
        """user_id가 없을 때 PIN 검증 테스트"""
        report_pin = ReportPin(
            pin_hash="some_hash",
        )
        # user_id가 설정되지 않음

        self.assertFalse(report_pin.verify_pin("1234"))

    def test_enabled_at_field(self):
        """enabled_at 필드 테스트"""
        now = timezone.now()
        report_pin = ReportPin.objects.create(
            user=self.user,
            pin_hash="test_hash",
            enabled_at=now,
        )

        self.assertIsNotNone(report_pin.enabled_at)
        self.assertEqual(report_pin.enabled_at, now)

    def test_update_pin_hash(self):
        """PIN 해시 업데이트 테스트"""
        old_pin = "1234"
        new_pin = "5678"

        report_pin = ReportPin.objects.create(
            user=self.user,
            pin_hash="temp_hash",
        )

        # 초기 PIN 설정
        old_hash = report_pin.get_pin_hash(old_pin)
        report_pin.pin_hash = old_hash
        report_pin.save()

        self.assertTrue(report_pin.verify_pin(old_pin))

        # PIN 변경
        new_hash = report_pin.get_pin_hash(new_pin)
        report_pin.pin_hash = new_hash
        report_pin.save()

        # 새 PIN은 통과, 이전 PIN은 실패
        self.assertTrue(report_pin.verify_pin(new_pin))
        self.assertFalse(report_pin.verify_pin(old_pin))

    def test_different_users_same_pin(self):
        """다른 사용자가 같은 PIN을 사용하면 다른 해시가 생성되는지 테스트"""
        user2 = User.objects.create_user(
            username="user2",
            password="pass123",
        )

        pin = "1234"

        report_pin1 = ReportPin.objects.create(
            user=self.user,
            pin_hash="temp1",
        )
        report_pin2 = ReportPin.objects.create(
            user=user2,
            pin_hash="temp2",
        )

        hash1 = report_pin1.get_pin_hash(pin)
        hash2 = report_pin2.get_pin_hash(pin)

        # 같은 PIN이라도 user_id가 salt로 사용되므로 다른 해시
        self.assertNotEqual(hash1, hash2)

    def test_cascade_delete_with_user(self):
        """사용자 삭제 시 ReportPin도 삭제되는지 테스트"""
        report_pin = ReportPin.objects.create(
            user=self.user,
            pin_hash="test_hash",
        )

        pin_id = report_pin.id

        # 사용자 삭제
        self.user.delete()

        # ReportPin도 삭제되었는지 확인
        self.assertFalse(ReportPin.objects.filter(id=pin_id).exists())

    def test_pin_hash_length_limit(self):
        """PIN 해시 최대 길이 테스트"""
        long_hash = "a" * 256  # max_length=256

        report_pin = ReportPin.objects.create(
            user=self.user,
            pin_hash=long_hash,
        )

        report_pin.refresh_from_db()
        self.assertEqual(len(report_pin.pin_hash), 256)
