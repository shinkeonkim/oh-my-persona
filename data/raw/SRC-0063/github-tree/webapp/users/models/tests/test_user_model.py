from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

import pytest

User = get_user_model()


class UserModelTests(TestCase):
    """User 모델 테스트"""

    def test_create_user_with_valid_username_and_password(self):
        """유효한 username과 password로 사용자 생성"""
        user = User.objects.create_user(
            username="test1234",
            password="password123",
        )
        self.assertEqual(user.username, "test1234")
        self.assertTrue(user.check_password("password123"))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_with_email(self):
        """email을 포함하여 사용자 생성"""
        user = User.objects.create_user(
            username="test1234",
            password="password123",
            email="test@example.com",
        )
        self.assertEqual(user.email, "test@example.com")

    def test_create_user_without_email(self):
        """email 없이 사용자 생성 (선택 사항)"""
        user = User.objects.create_user(
            username="test1234",
            password="password123",
        )
        self.assertIsNone(user.email)

    def test_create_superuser(self):
        """슈퍼유저 생성"""
        admin_user = User.objects.create_superuser(
            username="admin123",
            password="adminpass123",
        )
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_username_is_unique(self):
        """username은 unique해야 함"""
        User.objects.create_user(username="test1234", password="password123")

        with pytest.raises(IntegrityError):
            User.objects.create_user(username="test1234", password="different123")

    def test_username_field_is_username(self):
        """USERNAME_FIELD가 username으로 설정되어 있는지 확인"""
        self.assertEqual(User.USERNAME_FIELD, "username")

    def test_create_user_without_username_raises_error(self):
        """username 없이 사용자 생성 시 에러 발생"""
        with pytest.raises(ValueError, match="Username is required"):
            User.objects.create_user(username="", password="password123")
