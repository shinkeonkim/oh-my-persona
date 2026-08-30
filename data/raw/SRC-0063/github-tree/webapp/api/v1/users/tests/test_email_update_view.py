from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .test_helpers import get_error_details

User = get_user_model()


class EmailUpdateAPIViewTests(APITestCase):
    """Email 수정 API 테스트"""

    def setUp(self):
        self.url = reverse("email-update")
        self.user = User.objects.create_user(
            username="test1234",
            password="password123",
        )
        # JWT 토큰 생성
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

    def test_update_email_with_authentication(self):
        """인증된 사용자가 email 수정"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        data = {
            "email": "newemail@example.com",
        }
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Response는 UserDetailSerializer 형식
        self.assertIn("email", response.data)
        self.assertEqual(response.data.get("email"), "newemail@example.com")

        # DB에서 확인
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "newemail@example.com")

    def test_update_email_without_authentication(self):
        """인증 없이 email 수정 시도"""
        data = {
            "email": "newemail@example.com",
        }
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_email_with_invalid_email(self):
        """잘못된 email 형식"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        data = {
            "email": "invalid-email",
        }
        response = self.client.patch(self.url, data)
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, 422])
        error_data = get_error_details(response.data)
        self.assertIn("email", error_data)

    def test_update_email_without_email_field(self):
        """email 필드 없이 요청"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        data = {}
        response = self.client.patch(self.url, data)
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, 422])
        error_data = get_error_details(response.data)
        self.assertIn("email", error_data)

    def test_update_email_multiple_times(self):
        """email을 여러 번 수정"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        # 첫 번째 수정
        data = {"email": "first@example.com"}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 두 번째 수정
        data = {"email": "second@example.com"}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("email", response.data)
        self.assertEqual(response.data.get("email"), "second@example.com")
