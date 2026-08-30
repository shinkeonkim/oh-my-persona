from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from matchmakings.factories import ReferralFactory
from users.factories import UserFactory

User = get_user_model()


class LatestReferralAPIViewTest(APITestCase):
  """LatestReferralAPIView 테스트"""

  def setUp(self):
    """테스트 데이터 설정"""
    self.user = UserFactory(confirm_user=True)
    self.url = reverse("referral-latest")

  @patch("api.v1.matchmakings.views.referrals.latest_referral_api_view.ReferralService.get_latest_referral")
  def test_get_latest_referral_success(self, mock_get_latest):
    """최근 추천 조회 성공 테스트"""
    other_user = UserFactory(confirm_user=True)
    referral = ReferralFactory(user=self.user, referral_user=other_user, referred_at=timezone.now())
    mock_get_latest.return_value = referral

    self.client.force_authenticate(user=self.user)
    response = self.client.get(self.url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["id"], referral.id)
    mock_get_latest.assert_called_once_with(self.user, None)

  @patch("api.v1.matchmakings.views.referrals.latest_referral_api_view.ReferralService.get_latest_referral")
  def test_get_latest_referral_with_algorithm_type(self, mock_get_latest):
    """특정 알고리즘 타입의 최근 추천 조회 테스트"""
    other_user = UserFactory(confirm_user=True)
    referral = ReferralFactory(user=self.user, referral_user=other_user, referred_at=timezone.now())
    mock_get_latest.return_value = referral

    self.client.force_authenticate(user=self.user)
    response = self.client.get(self.url, {"algorithm_type": "compatibility"})

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["id"], referral.id)
    mock_get_latest.assert_called_once_with(self.user, "compatibility")

  @patch("api.v1.matchmakings.views.referrals.latest_referral_api_view.ReferralService.get_latest_referral")
  def test_get_latest_referral_with_location_algorithm(self, mock_get_latest):
    """location 알고리즘의 최근 추천 조회 테스트"""
    other_user = UserFactory(confirm_user=True)
    referral = ReferralFactory(user=self.user, referral_user=other_user, referred_at=timezone.now())
    mock_get_latest.return_value = referral

    self.client.force_authenticate(user=self.user)
    response = self.client.get(self.url, {"algorithm_type": "location"})

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    mock_get_latest.assert_called_once_with(self.user, "location")

  @patch("api.v1.matchmakings.views.referrals.latest_referral_api_view.ReferralService.get_latest_referral")
  def test_get_latest_referral_not_found(self, mock_get_latest):
    """추천이 없을 때 200 OK with null data 테스트"""
    mock_get_latest.return_value = None

    self.client.force_authenticate(user=self.user)
    response = self.client.get(self.url)

    # View는 None을 serializer에 전달하여 null 값으로 직렬화됨
    self.assertEqual(response.status_code, status.HTTP_200_OK)

  def test_get_latest_referral_unauthenticated(self):
    """인증되지 않은 사용자의 요청은 401 에러 테스트"""
    response = self.client.get(self.url)

    self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

  @patch("api.v1.matchmakings.views.referrals.latest_referral_api_view.ReferralService.get_latest_referral")
  def test_get_latest_referral_without_algorithm_type(self, mock_get_latest):
    """algorithm_type 없이 조회 시 전체 최근 추천 조회 테스트"""
    other_user = UserFactory(confirm_user=True)
    referral = ReferralFactory(user=self.user, referral_user=other_user, referred_at=timezone.now())
    mock_get_latest.return_value = referral

    self.client.force_authenticate(user=self.user)
    response = self.client.get(self.url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    # algorithm_type이 None으로 전달되어야 함
    mock_get_latest.assert_called_once_with(self.user, None)

  @patch("api.v1.matchmakings.views.referrals.latest_referral_api_view.ReferralService.get_latest_referral")
  def test_get_latest_referral_with_all_algorithm_types(self, mock_get_latest):
    """모든 알고리즘 타입으로 최근 추천 조회 테스트"""
    algorithms = ["compatibility", "location", "age", "job", "mbti", "random"]

    for algorithm in algorithms:
      other_user = UserFactory(confirm_user=True)
      referral = ReferralFactory(user=self.user, referral_user=other_user, referred_at=timezone.now())
      mock_get_latest.return_value = referral

      self.client.force_authenticate(user=self.user)
      response = self.client.get(self.url, {"algorithm_type": algorithm})

      self.assertEqual(response.status_code, status.HTTP_200_OK, f"Failed for algorithm: {algorithm}")
      mock_get_latest.assert_called_with(self.user, algorithm)

  def test_get_latest_referral_method_not_allowed(self):
    """GET 이외의 메서드는 허용되지 않음 테스트"""
    self.client.force_authenticate(user=self.user)

    # POST 요청
    response = self.client.post(self.url, {}, format="json")
    self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # DELETE 요청
    response = self.client.delete(self.url)
    self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

  @patch("api.v1.matchmakings.views.referrals.latest_referral_api_view.ReferralService.get_latest_referral")
  def test_get_latest_referral_returns_referral_user_profile(self, mock_get_latest):
    """최근 추천 응답에 referral_user 프로필 정보가 포함되는지 테스트"""
    other_user = UserFactory(confirm_user=True)
    referral = ReferralFactory(user=self.user, referral_user=other_user, referred_at=timezone.now())
    mock_get_latest.return_value = referral

    self.client.force_authenticate(user=self.user)
    response = self.client.get(self.url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertIn("referral_user", response.data)
    # referral_user는 nested serializer로 반환되므로 dict인지 확인
    self.assertIsInstance(response.data["referral_user"], dict)
    self.assertEqual(response.data["referral_user"]["id"], other_user.id)

  @patch("api.v1.matchmakings.views.referrals.latest_referral_api_view.ReferralService.get_latest_referral")
  def test_get_latest_referral_with_invalid_algorithm_type(self, mock_get_latest):
    """유효하지 않은 algorithm_type은 무시되고 조회되는지 테스트"""
    other_user = UserFactory(confirm_user=True)
    referral = ReferralFactory(user=self.user, referral_user=other_user, referred_at=timezone.now())
    mock_get_latest.return_value = referral

    self.client.force_authenticate(user=self.user)
    # 유효하지 않은 algorithm_type (서비스에서 처리)
    response = self.client.get(self.url, {"algorithm_type": "invalid_algo"})

    # View는 쿼리 파라미터를 그대로 전달, 서비스에서 처리
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    mock_get_latest.assert_called_once_with(self.user, "invalid_algo")

  @patch("api.v1.matchmakings.views.referrals.latest_referral_api_view.ReferralService.get_latest_referral")
  def test_get_latest_referral_returns_timestamp(self, mock_get_latest):
    """최근 추천 응답에 referred_at 타임스탬프가 포함되는지 테스트"""
    other_user = UserFactory(confirm_user=True)
    referral = ReferralFactory(user=self.user, referral_user=other_user, referred_at=timezone.now())
    mock_get_latest.return_value = referral

    self.client.force_authenticate(user=self.user)
    response = self.client.get(self.url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertIn("referred_at", response.data)
    self.assertIsNotNone(response.data["referred_at"])
