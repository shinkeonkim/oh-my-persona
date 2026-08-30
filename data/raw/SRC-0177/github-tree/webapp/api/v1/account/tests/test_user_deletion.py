from unittest.mock import patch

from allauth.socialaccount.models import SocialAccount, SocialToken
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class UserDeletionTests(APITestCase):
    def setUp(self):
        # 테스트 사용자 생성
        self.user = User.objects.create_user(
            email="test@example.com", password="password123", username="testuser"
        )

        # 소셜 계정 생성
        self.social_account = SocialAccount.objects.create(
            user=self.user, provider="kakao", uid="12345678"
        )

        # 소셜 토큰 생성
        self.social_token = SocialToken.objects.create(
            account=self.social_account,
            token="test_access_token",
            token_secret="test_refresh_token",
        )

        # 클라이언트 및 URL 설정
        self.client = APIClient()
        self.url = reverse("api:v1:account:user_delete")

        # 인증
        self.client.force_authenticate(user=self.user)

    @patch("requests.post")
    def test_delete_user(self, mock_post):
        # kakao API 호출 모킹
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"id": 12345678}

        # KAKAO_ADMIN_KEY 설정을 위한 패치
        with patch("django.conf.settings.KAKAO_ADMIN_KEY", "test_admin_key"):
            # 사용자 탈퇴 요청
            response = self.client.delete(self.url)

            # 응답 확인
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

            # 사용자 및 소셜 계정이 삭제되었는지 확인
            # 테스트 전에 ID 저장
            user_id = self.user.id
            account_id = self.social_account.id

            self.assertEqual(User.objects.filter(id=user_id).count(), 0)
            self.assertEqual(SocialAccount.objects.filter(user_id=user_id).count(), 0)
            self.assertEqual(
                SocialToken.objects.filter(account_id=account_id).count(), 0
            )

            # kakao API가 호출되었는지 확인
            mock_post.assert_called_once()
            # 어드민 키를 사용했는지 확인
            self.assertTrue(
                "KakaoAK" in mock_post.call_args[1]["headers"]["Authorization"]
            )

    def test_delete_user_unauthenticated(self):
        # 로그아웃
        self.client.force_authenticate(user=None)

        # 사용자 탈퇴 요청
        response = self.client.delete(self.url)

        # 응답 확인 (403 반환)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 사용자 및 소셜 계정이 삭제되지 않았는지 확인
        self.assertEqual(User.objects.filter(id=self.user.id).count(), 1)
        self.assertEqual(SocialAccount.objects.filter(user=self.user).count(), 1)
        self.assertEqual(
            SocialToken.objects.filter(account=self.social_account).count(), 1
        )

    @patch("requests.post")
    def test_delete_user_kakao_api_error(self, mock_post):
        # Kakao API 오류 모킹
        mock_post.return_value.status_code = 400
        mock_post.return_value.text = '{"msg":"Invalid target id"}'

        # 사용자 탈퇴 요청
        response = self.client.delete(self.url)

        # 응답 확인 - API 오류에도 사용자 삭제는 성공해야 함
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # 사용자 및 소셜 계정이 삭제되었는지 확인
        # 테스트 전에 ID 저장
        user_id = self.user.id
        account_id = self.social_account.id

        self.assertEqual(User.objects.filter(id=user_id).count(), 0)
        self.assertEqual(SocialAccount.objects.filter(user_id=user_id).count(), 0)
        self.assertEqual(SocialToken.objects.filter(account_id=account_id).count(), 0)
