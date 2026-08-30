from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

import pytest

User = get_user_model()


class UsernameValidatorTests(TestCase):
    """Username validator 테스트"""

    def test_valid_username_with_letters_and_numbers(self):
        """유효한 username: 영문과 숫자 조합"""
        user = User(username="test1234", email="test@example.com")
        user.set_password("password123")
        user.full_clean()  # 모든 validator 실행
        self.assertEqual(user.username, "test1234")

    def test_valid_username_minimum_length(self):
        """유효한 username: 최소 4자리"""
        user = User(username="abc1", email="test@example.com")
        user.set_password("password123")
        user.full_clean()
        self.assertEqual(user.username, "abc1")

    def test_invalid_username_too_short(self):
        """무효한 username: 4자리 미만"""
        user = User(username="ab1", email="test@example.com")
        with pytest.raises(ValidationError) as exc_info:
            user.full_clean()
        self.assertIn("username", exc_info.value.error_dict)

    def test_invalid_username_only_letters(self):
        """무효한 username: 영문만 있음 (숫자 없음)"""
        user = User(username="testuser", email="test@example.com")
        with pytest.raises(ValidationError) as exc_info:
            user.full_clean()
        self.assertIn("username", exc_info.value.error_dict)

    def test_invalid_username_only_numbers(self):
        """무효한 username: 숫자만 있음 (영문 없음)"""
        user = User(username="12345", email="test@example.com")
        with pytest.raises(ValidationError) as exc_info:
            user.full_clean()
        self.assertIn("username", exc_info.value.error_dict)

    def test_invalid_username_with_special_characters(self):
        """무효한 username: 특수문자 포함"""
        user = User(username="test@123", email="test@example.com")
        with pytest.raises(ValidationError) as exc_info:
            user.full_clean()
        self.assertIn("username", exc_info.value.error_dict)

    def test_invalid_username_with_spaces(self):
        """무효한 username: 공백 포함"""
        user = User(username="test 123", email="test@example.com")
        with pytest.raises(ValidationError) as exc_info:
            user.full_clean()
        self.assertIn("username", exc_info.value.error_dict)

    def test_valid_username_mixed_case(self):
        """유효한 username: 대소문자 혼합"""
        user = User(username="Test1234", email="test@example.com")
        user.set_password("password123")
        user.full_clean()
        self.assertEqual(user.username, "Test1234")

    def test_valid_username_long(self):
        """유효한 username: 긴 username"""
        user = User(username="testuser12345678", email="test@example.com")
        user.set_password("password123")
        user.full_clean()
        self.assertEqual(user.username, "testuser12345678")
