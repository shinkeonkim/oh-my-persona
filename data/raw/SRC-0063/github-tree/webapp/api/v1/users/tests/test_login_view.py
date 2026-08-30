from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class LoginAPIViewTests(APITestCase):
    """로그인 API 테스트 (dj-rest-auth의 login endpoint 사용)"""

    def setUp(self):
        self.url = reverse("rest_login")
        self.user = User.objects.create_user(
            username="test1234",
            password="password123",
        )

    def test_login_with_valid_credentials(self):
        """유효한 인증정보로 로그인"""
        data = {
            "username": "test1234",
            "password": "password123",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["username"], "test1234")

    def test_login_with_invalid_password(self):
        """잘못된 비밀번호로 로그인 시도"""
        data = {
            "username": "test1234",
            "password": "wrongpassword123",
        }
        response = self.client.post(self.url, data)
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, 422])

    def test_login_with_invalid_username(self):
        """존재하지 않는 username으로 로그인 시도"""
        data = {
            "username": "nonexistent123",
            "password": "password123",
        }
        response = self.client.post(self.url, data)
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, 422])

    def test_login_without_username(self):
        """username 없이 로그인 시도"""
        data = {
            "password": "password123",
        }
        response = self.client.post(self.url, data)
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, 422])

    def test_login_without_password(self):
        """password 없이 로그인 시도"""
        data = {
            "username": "test1234",
        }
        response = self.client.post(self.url, data)
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, 422])
