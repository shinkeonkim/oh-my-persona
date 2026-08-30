from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from .test_helpers import get_error_details

User = get_user_model()


class RegistrationAPIViewTests(APITestCase):
    """회원가입 API 테스트 (dj-rest-auth의 registration endpoint 사용)"""

    def setUp(self):
        self.url = reverse("rest_register")

    def test_register_with_valid_data(self):
        """유효한 데이터로 회원가입"""
        data = {
            "username": "newuser123",
            "password1": "password123",
            "password2": "password123",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["username"], "newuser123")

        # DB에 사용자가 생성되었는지 확인
        self.assertTrue(User.objects.filter(username="newuser123").exists())

    def test_register_with_email(self):
        """email을 포함하여 회원가입"""
        data = {
            "username": "newuser123",
            "password1": "password123",
            "password2": "password123",
            "email": "test@example.com",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(username="newuser123")
        self.assertEqual(user.email, "test@example.com")

    def test_register_without_email(self):
        """email 없이 회원가입"""
        data = {
            "username": "newuser123",
            "password1": "password123",
            "password2": "password123",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(username="newuser123")
        self.assertIn(user.email, [None, ""])

    def test_register_with_invalid_username_too_short(self):
        """무효한 username: 4자리 미만"""
        data = {
            "username": "ab1",
            "password1": "password123",
            "password2": "password123",
        }
        response = self.client.post(self.url, data)
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, 422])
        error_data = get_error_details(response.data)
        self.assertIn("username", error_data)

    def test_register_with_invalid_username_only_letters(self):
        """무효한 username: 영문만"""
        data = {
            "username": "testuser",
            "password1": "password123",
            "password2": "password123",
        }
        response = self.client.post(self.url, data)
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, 422])
        error_data = get_error_details(response.data)
        self.assertIn("username", error_data)

    def test_register_with_invalid_username_only_numbers(self):
        """무효한 username: 숫자만"""
        data = {
            "username": "12345",
            "password1": "password123",
            "password2": "password123",
        }
        response = self.client.post(self.url, data)
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, 422])
        error_data = get_error_details(response.data)
        self.assertIn("username", error_data)

    def test_register_with_invalid_password_too_short(self):
        """무효한 password: 8자리 미만"""
        data = {
            "username": "test1234",
            "password1": "pass123",
            "password2": "pass123",
        }
        response = self.client.post(self.url, data)
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, 422])
        error_data = get_error_details(response.data)
        self.assertIn("password1", error_data)

    def test_register_with_invalid_password_only_letters(self):
        """무효한 password: 영문만"""
        data = {
            "username": "test1234",
            "password1": "password",
            "password2": "password",
        }
        response = self.client.post(self.url, data)
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, 422])
        error_data = get_error_details(response.data)
        self.assertIn("password1", error_data)

    def test_register_with_invalid_password_only_numbers(self):
        """무효한 password: 숫자만"""
        data = {
            "username": "test1234",
            "password1": "12345678",
            "password2": "12345678",
        }
        response = self.client.post(self.url, data)
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, 422])
        error_data = get_error_details(response.data)
        self.assertIn("password1", error_data)

    def test_register_with_duplicate_username(self):
        """중복된 username으로 회원가입 시도"""
        User.objects.create_user(username="existing123", password="password123")

        data = {
            "username": "existing123",
            "password1": "password123",
            "password2": "password123",
        }
        response = self.client.post(self.url, data)
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, 422])

    def test_register_with_password_mismatch(self):
        """비밀번호 불일치"""
        data = {
            "username": "test1234",
            "password1": "password123",
            "password2": "different123",
        }
        response = self.client.post(self.url, data)
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, 422])
