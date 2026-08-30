from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class CheckUsernameAPIViewTests(APITestCase):
    """Username 중복 확인 API 테스트"""

    def setUp(self):
        self.url = reverse("check-username")
        User.objects.create_user(username="existing123", password="password123")

    def test_check_existing_username(self):
        """이미 존재하는 username 확인"""
        response = self.client.get(self.url, {"username": "existing123"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["exists"], True)

    def test_check_available_username(self):
        """사용 가능한 username 확인"""
        response = self.client.get(self.url, {"username": "available123"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["exists"], False)

    def test_check_username_without_parameter(self):
        """username 파라미터 없이 요청"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_check_username_with_empty_string(self):
        """빈 문자열로 요청"""
        response = self.client.get(self.url, {"username": ""})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_check_username_case_sensitive(self):
        """대소문자 구분 확인"""
        # existing123은 존재
        response = self.client.get(self.url, {"username": "Existing123"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 대소문자가 다르므로 exists는 False여야 함
        self.assertEqual(response.data["exists"], False)

    def test_check_username_allows_anonymous_access(self):
        """익명 사용자도 접근 가능"""
        # 인증 없이 요청
        response = self.client.get(self.url, {"username": "test123"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
