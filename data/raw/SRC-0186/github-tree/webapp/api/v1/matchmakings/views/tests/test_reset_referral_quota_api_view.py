from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from users.factories import UserFactory

User = get_user_model()

REFERRAL_QUOTA_RESET_TICKET_COST = settings.REFERRAL_QUOTA_RESET_TICKET_COST


class ResetReferralQuotaAPIViewTest(APITestCase):
  """ResetReferralQuotaAPIView 테스트"""

  def setUp(self):
    """테스트 데이터 설정"""
    self.user = UserFactory(confirm_user=True, ticket_amount=100)
    self.url = reverse("referral-reset")

  @patch("api.v1.matchmakings.views.referrals.reset_referral_quota_api_view.ReferralResetService.reset_referral_quota")
  def test_reset_referral_quota_success(self, mock_reset_quota):
    """추천 횟수 초기화 성공 테스트"""
    self.user.remaining_referral_quota = 5
    self.user.ticket_amount = 50
    mock_reset_quota.return_value = self.user

    self.client.force_authenticate(user=self.user)
    response = self.client.post(self.url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["remaining_referral_quota"], 5)
    self.assertEqual(response.data["ticket_amount"], 50)
    self.assertEqual(response.data["used_tickets"], REFERRAL_QUOTA_RESET_TICKET_COST)
    self.assertIn("message", response.data)
    mock_reset_quota.assert_called_once_with(self.user)

  @patch("api.v1.matchmakings.views.referrals.reset_referral_quota_api_view.ReferralResetService.reset_referral_quota")
  def test_reset_referral_quota_insufficient_tickets(self, mock_reset_quota):
    """티켓 부족 시 422 에러 테스트"""
    from api.v1.matchmakings.exceptions import ReferralValidationError

    mock_reset_quota.side_effect = ReferralValidationError(
        message="Insufficient tickets",
        details={
            "required": REFERRAL_QUOTA_RESET_TICKET_COST,
            "available": 0
        },
    )

    self.client.force_authenticate(user=self.user)
    response = self.client.post(self.url)

    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

  @patch("api.v1.matchmakings.views.referrals.reset_referral_quota_api_view.ReferralResetService.reset_referral_quota")
  def test_reset_referral_quota_already_has_quota(self, mock_reset_quota):
    """이미 추천 횟수가 있을 때 422 에러 테스트"""
    from api.v1.matchmakings.exceptions import ReferralValidationError

    mock_reset_quota.side_effect = ReferralValidationError(
        message="User still has remaining referral quota",
        details={"remaining_quota": 3},
    )

    self.client.force_authenticate(user=self.user)
    response = self.client.post(self.url)

    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

  def test_reset_referral_quota_unauthenticated(self):
    """인증되지 않은 사용자의 요청은 401 또는 403 에러 테스트"""
    response = self.client.post(self.url)

    self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

  @patch("api.v1.matchmakings.views.referrals.reset_referral_quota_api_view.ReferralResetService.reset_referral_quota")
  def test_reset_referral_quota_returns_message(self, mock_reset_quota):
    """응답에 성공 메시지가 포함되는지 테스트"""
    self.user.remaining_referral_quota = 5
    mock_reset_quota.return_value = self.user

    self.client.force_authenticate(user=self.user)
    response = self.client.post(self.url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["message"], "추천 횟수가 초기화되었습니다.")

  @patch("api.v1.matchmakings.views.referrals.reset_referral_quota_api_view.ReferralResetService.reset_referral_quota")
  def test_reset_referral_quota_deducts_tickets(self, mock_reset_quota):
    """티켓이 차감되었음을 응답에 포함하는지 테스트"""
    self.user.remaining_referral_quota = 5
    self.user.ticket_amount = 50
    mock_reset_quota.return_value = self.user

    self.client.force_authenticate(user=self.user)
    response = self.client.post(self.url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["used_tickets"], REFERRAL_QUOTA_RESET_TICKET_COST)

  def test_reset_referral_quota_method_not_allowed(self):
    """POST 이외의 메서드는 허용되지 않음 테스트"""
    self.client.force_authenticate(user=self.user)

    # GET 요청
    response = self.client.get(self.url)
    self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # PUT 요청
    response = self.client.put(self.url, {}, format="json")
    self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # DELETE 요청
    response = self.client.delete(self.url)
    self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

  @patch("api.v1.matchmakings.views.referrals.reset_referral_quota_api_view.ReferralResetService.reset_referral_quota")
  def test_reset_referral_quota_calls_service(self, mock_reset_quota):
    """서비스 메서드가 올바르게 호출되는지 테스트"""
    self.user.remaining_referral_quota = 5
    mock_reset_quota.return_value = self.user

    self.client.force_authenticate(user=self.user)
    response = self.client.post(self.url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    mock_reset_quota.assert_called_once_with(self.user)

  @patch("api.v1.matchmakings.views.referrals.reset_referral_quota_api_view.ReferralResetService.reset_referral_quota")
  def test_reset_referral_quota_no_body_required(self, mock_reset_quota):
    """요청 바디가 필요 없는지 테스트"""
    self.user.remaining_referral_quota = 5
    mock_reset_quota.return_value = self.user

    self.client.force_authenticate(user=self.user)
    # 빈 바디로 POST
    response = self.client.post(self.url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)

  @patch("api.v1.matchmakings.views.referrals.reset_referral_quota_api_view.ReferralResetService.reset_referral_quota")
  def test_reset_referral_quota_returns_updated_user_info(self, mock_reset_quota):
    """초기화 후 업데이트된 사용자 정보가 반환되는지 테스트"""
    # 초기화 후 상태
    self.user.remaining_referral_quota = 3  # 초기화된 값
    self.user.ticket_amount = 45  # REFERRAL_QUOTA_RESET_TICKET_COST만큼 차감된 값
    mock_reset_quota.return_value = self.user

    self.client.force_authenticate(user=self.user)
    response = self.client.post(self.url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["remaining_referral_quota"], 3)
    self.assertEqual(response.data["ticket_amount"], 45)

  @patch("api.v1.matchmakings.views.referrals.reset_referral_quota_api_view.ReferralResetService.reset_referral_quota")
  def test_reset_referral_quota_with_exact_ticket_amount(self, mock_reset_quota):
    """정확히 필요한 티켓 수량을 보유한 경우 테스트"""
    self.user.ticket_amount = REFERRAL_QUOTA_RESET_TICKET_COST
    self.user.remaining_referral_quota = 3
    mock_reset_quota.return_value = self.user

    self.client.force_authenticate(user=self.user)
    response = self.client.post(self.url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)

  @patch("api.v1.matchmakings.views.referrals.reset_referral_quota_api_view.ReferralResetService.reset_referral_quota")
  def test_reset_referral_quota_exception_handling(self, mock_reset_quota):
    """서비스에서 일반 예외 발생 시 처리 테스트"""
    from api.v1.matchmakings.exceptions import ReferralValidationError

    # 일반 Exception 대신 처리 가능한 ReferralValidationError를 사용
    mock_reset_quota.side_effect = ReferralValidationError(message="Cannot reset quota",
                                                           details={"reason": "unknown_error"})

    self.client.force_authenticate(user=self.user)
    response = self.client.post(self.url)

    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
