from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from matchmakings.factories import ReferralFactory
from users.factories import UserFactory

User = get_user_model()


class CreateReferralAPIViewTest(APITestCase):
  """CreateReferralAPIView 테스트"""

  def setUp(self):
    """테스트 데이터 설정"""
    self.user = UserFactory(confirm_user=True)
    self.url = reverse("referral-list-create")

  @patch("matchmakings.tasks.generate_referral_llm_messages_task.generate_referral_llm_messages.delay")
  @patch("api.v1.matchmakings.views.referrals.create_referral_api_view.ReferralService.create_referral")
  def test_create_referral_success(self, mock_create_referral, mock_task):
    """추천 생성 성공 테스트"""
    other_user = UserFactory(confirm_user=True)
    referral = ReferralFactory(user=self.user, referral_user=other_user)
    mock_create_referral.return_value = referral

    data = {"algorithm_type": "RandomAlgorithm"}

    self.client.force_authenticate(user=self.user)
    response = self.client.post(self.url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    self.assertEqual(response.data["id"], referral.id)
    mock_create_referral.assert_called_once_with(self.user, "RandomAlgorithm")
    mock_task.assert_called_once_with(referral.id)

  @patch("matchmakings.tasks.generate_referral_llm_messages_task.generate_referral_llm_messages.delay")
  @patch("api.v1.matchmakings.views.referrals.create_referral_api_view.ReferralService.create_referral")
  def test_create_referral_with_location_algorithm(self, mock_create_referral, mock_task):
    """location 알고리즘으로 추천 생성 테스트"""
    other_user = UserFactory(confirm_user=True)
    referral = ReferralFactory(user=self.user, referral_user=other_user)
    mock_create_referral.return_value = referral

    data = {"algorithm_type": "AAlgorithm"}

    self.client.force_authenticate(user=self.user)
    response = self.client.post(self.url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    mock_create_referral.assert_called_once_with(self.user, "AAlgorithm")
    mock_task.assert_called_once_with(referral.id)

  def test_create_referral_invalid_algorithm_type(self):
    """유효하지 않은 algorithm_type으로 추천 생성 시 400 에러 테스트"""
    data = {"algorithm_type": "invalid_algorithm"}

    self.client.force_authenticate(user=self.user)
    response = self.client.post(self.url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

  def test_create_referral_missing_algorithm_type(self):
    """algorithm_type 누락 시 400 에러 테스트"""
    data = {}

    self.client.force_authenticate(user=self.user)
    response = self.client.post(self.url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

  @patch("api.v1.matchmakings.views.referrals.create_referral_api_view.ReferralService.create_referral")
  def test_create_referral_no_more_referrals_available(self, mock_create_referral):
    """더 이상 추천할 사용자가 없을 때 404 에러 테스트"""
    mock_create_referral.return_value = None

    data = {"algorithm_type": "RandomAlgorithm"}

    self.client.force_authenticate(user=self.user)
    response = self.client.post(self.url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    self.assertIn("algorithm_type", response.data["details"])

  def test_create_referral_unauthenticated(self):
    """인증되지 않은 사용자의 요청은 401 에러 테스트"""
    data = {"algorithm_type": "RandomAlgorithm"}

    response = self.client.post(self.url, data, format="json")

    self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

  @patch("matchmakings.tasks.generate_referral_llm_messages_task.generate_referral_llm_messages.delay")
  @patch("api.v1.matchmakings.views.referrals.create_referral_api_view.ReferralService.create_referral")
  def test_create_referral_with_different_algorithms(self, mock_create_referral, mock_task):
    """다양한 알고리즘 타입으로 추천 생성 테스트"""
    algorithms = ["RandomAlgorithm", "AAlgorithm", "BAlgorithm", "CAlgorithm"]

    for algorithm in algorithms:
      other_user = UserFactory(confirm_user=True)
      referral = ReferralFactory(user=self.user, referral_user=other_user)
      mock_create_referral.return_value = referral

      data = {"algorithm_type": algorithm}

      self.client.force_authenticate(user=self.user)
      response = self.client.post(self.url, data, format="json")

      self.assertEqual(response.status_code, status.HTTP_201_CREATED, f"Failed for algorithm: {algorithm}")
      mock_create_referral.assert_called_with(self.user, algorithm)
      mock_task.assert_called_with(referral.id)

  def test_create_referral_method_not_allowed(self):
    """POST 이외의 메서드는 허용되지 않음 테스트"""
    self.client.force_authenticate(user=self.user)

    # GET 요청
    response = self.client.get(self.url)
    self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # PUT 요청
    response = self.client.put(self.url, {}, format="json")
    self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

  @patch("api.v1.matchmakings.views.referrals.create_referral_api_view.ReferralService.create_referral")
  def test_create_referral_validates_serializer(self, mock_create_referral):
    """시리얼라이저 검증 테스트"""
    # 빈 문자열
    data = {"algorithm_type": ""}

    self.client.force_authenticate(user=self.user)
    response = self.client.post(self.url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    mock_create_referral.assert_not_called()

  @patch("matchmakings.tasks.generate_referral_llm_messages_task.generate_referral_llm_messages.delay")
  @patch("api.v1.matchmakings.views.referrals.create_referral_api_view.ReferralService.create_referral")
  def test_create_referral_returns_referral_user_profile(self, mock_create_referral, mock_task):
    """추천 생성 응답에 referral_user 프로필 정보가 포함되는지 테스트"""
    other_user = UserFactory(confirm_user=True)
    referral = ReferralFactory(user=self.user, referral_user=other_user)
    mock_create_referral.return_value = referral

    data = {"algorithm_type": "RandomAlgorithm"}

    self.client.force_authenticate(user=self.user)
    response = self.client.post(self.url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    self.assertIn("referral_user", response.data)
    # referral_user는 nested serializer로 반환되므로 dict인지 확인
    self.assertIsInstance(response.data["referral_user"], dict)
    mock_task.assert_called_once_with(referral.id)
    self.assertEqual(response.data["referral_user"]["id"], other_user.id)

  @patch("api.v1.matchmakings.views.referrals.create_referral_api_view.ReferralService.create_referral")
  def test_create_referral_exception_handling(self, mock_create_referral):
    """서비스에서 예외 발생 시 처리 테스트"""
    from api.v1.matchmakings.exceptions import ReferralValidationError

    mock_create_referral.side_effect = ReferralValidationError(message="Cannot create referral",
                                                               details={"reason": "quota_exceeded"})

    data = {"algorithm_type": "RandomAlgorithm"}

    self.client.force_authenticate(user=self.user)
    response = self.client.post(self.url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
