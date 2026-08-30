from django.test import TestCase

from rest_framework.test import APIRequestFactory

from api.v1.users.serializers import RegisterSerializer


class RegisterSerializerTests(TestCase):
    """RegisterSerializer 테스트"""

    def setUp(self):
        self.factory = APIRequestFactory()

    def test_valid_registration_data(self):
        """유효한 회원가입 데이터"""
        data = {
            "username": "test1234",
            "password1": "password123",
            "password2": "password123",
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_registration_with_email(self):
        """email을 포함한 회원가입"""
        data = {
            "username": "test1234",
            "password1": "password123",
            "password2": "password123",
            "email": "test@example.com",
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_registration_without_email(self):
        """email 없이 회원가입 (선택 사항)"""
        data = {
            "username": "test1234",
            "password1": "password123",
            "password2": "password123",
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_username_too_short(self):
        """무효한 username: 4자리 미만"""
        data = {
            "username": "ab1",
            "password1": "password123",
            "password2": "password123",
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("username", serializer.errors)

    def test_invalid_username_only_letters(self):
        """무효한 username: 영문만 있음"""
        data = {
            "username": "testuser",
            "password1": "password123",
            "password2": "password123",
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("username", serializer.errors)

    def test_invalid_username_only_numbers(self):
        """무효한 username: 숫자만 있음"""
        data = {
            "username": "12345",
            "password1": "password123",
            "password2": "password123",
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("username", serializer.errors)

    def test_invalid_username_with_special_characters(self):
        """무효한 username: 특수문자 포함"""
        data = {
            "username": "test@123",
            "password1": "password123",
            "password2": "password123",
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("username", serializer.errors)

    def test_invalid_password_too_short(self):
        """무효한 password: 8자리 미만"""
        data = {
            "username": "test1234",
            "password1": "pass123",
            "password2": "pass123",
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password1", serializer.errors)

    def test_invalid_password_only_letters(self):
        """무효한 password: 영문만 있음"""
        data = {
            "username": "test1234",
            "password1": "password",
            "password2": "password",
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password1", serializer.errors)

    def test_invalid_password_only_numbers(self):
        """무효한 password: 숫자만 있음"""
        data = {
            "username": "test1234",
            "password1": "12345678",
            "password2": "12345678",
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password1", serializer.errors)

    def test_password_mismatch(self):
        """비밀번호 불일치"""
        data = {
            "username": "test1234",
            "password1": "password123",
            "password2": "different123",
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_missing_username(self):
        """username 누락"""
        data = {
            "password1": "password123",
            "password2": "password123",
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("username", serializer.errors)

    def test_missing_password(self):
        """password 누락"""
        data = {
            "username": "test1234",
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
