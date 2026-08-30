from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework.test import APIRequestFactory

from api.v1.users.serializers import LoginSerializer

User = get_user_model()


class LoginSerializerTests(TestCase):
    """LoginSerializer 테스트"""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username="test1234",
            password="password123",
        )

    def test_valid_login_data(self):
        """유효한 로그인 데이터"""
        request = self.factory.post("/fake-url/")
        data = {
            "username": "test1234",
            "password": "password123",
        }
        serializer = LoginSerializer(data=data, context={"request": request})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["user"], self.user)

    def test_invalid_password(self):
        """잘못된 비밀번호"""
        request = self.factory.post("/fake-url/")
        data = {
            "username": "test1234",
            "password": "wrongpassword123",
        }
        serializer = LoginSerializer(data=data, context={"request": request})
        self.assertFalse(serializer.is_valid())

    def test_invalid_username(self):
        """존재하지 않는 username"""
        request = self.factory.post("/fake-url/")
        data = {
            "username": "nonexistent123",
            "password": "password123",
        }
        serializer = LoginSerializer(data=data, context={"request": request})
        self.assertFalse(serializer.is_valid())

    def test_missing_username(self):
        """username 누락"""
        request = self.factory.post("/fake-url/")
        data = {
            "password": "password123",
        }
        serializer = LoginSerializer(data=data, context={"request": request})
        self.assertFalse(serializer.is_valid())
        self.assertIn("username", serializer.errors)

    def test_missing_password(self):
        """password 누락"""
        request = self.factory.post("/fake-url/")
        data = {
            "username": "test1234",
        }
        serializer = LoginSerializer(data=data, context={"request": request})
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_email_field_not_used(self):
        """email 필드가 사용되지 않음"""
        request = self.factory.post("/fake-url/")
        data = {
            "username": "test1234",
            "password": "password123",
            "email": "test@example.com",  # 무시되어야 함
        }
        serializer = LoginSerializer(data=data, context={"request": request})
        self.assertTrue(serializer.is_valid())
        # email은 serializer에 정의되어 있지 않음
        self.assertIsNone(getattr(serializer, "email", None))
