from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from matchmakings.factories import ReferralFactory
from users.factories import UserFactory

User = get_user_model()

MATCHING_TICKET_COST = settings.MATCHING_TICKET_COST


class CreateMatchingAPIViewTest(APITestCase):
  """CreateMatchingAPIView 테스트"""

  def setUp(self):
    """테스트 데이터 설정"""
    self.user = UserFactory(confirm_user=True, ticket_amount=100)
    self.other_user = UserFactory(confirm_user=True)
    self.url = reverse("matching-create")

  @patch("api.v1.matchmakings.views.matchings.create_matching_api_view.MatchingService.create_matching_from_referral")
  @patch("api.v1.matchmakings.views.matchings.create_matching_api_view.MatchingService.check_ticket_availability")
  def test_create_matching_success(self, mock_check_ticket, mock_create_matching):
    """매칭 생성 성공 테스트"""
    referral = ReferralFactory(user=self.user, referral_user=self.other_user)

    mock_check_ticket.return_value = True
    # mock_matching은 referral을 그대로 반환 (이미 생성된 referral 재사용)
    mock_create_matching.return_value = referral

    data = {"referral_id": referral.id}

    self.client.force_authenticate(user=self.user)
    response = self.client.post(self.url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    mock_check_ticket.assert_called_once_with(self.user, MATCHING_TICKET_COST)
    mock_create_matching.assert_called_once_with(self.user, referral.id, MATCHING_TICKET_COST)

  def test_create_matching_invalid_referral_id(self):
    """유효하지 않은 referral_id로 매칭 생성 시 400 에러 테스트"""
    data = {"referral_id": "invalid"}

    self.client.force_authenticate(user=self.user)
    response = self.client.post(self.url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

  def test_create_matching_missing_referral_id(self):
    """referral_id 누락 시 400 에러 테스트"""
    data = {}

    self.client.force_authenticate(user=self.user)
    response = self.client.post(self.url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

  @patch("api.v1.matchmakings.views.matchings.create_matching_api_view.MatchingService.check_ticket_availability")
  def test_create_matching_insufficient_tickets(self, mock_check_ticket):
    """티켓 부족 시 400 에러 테스트"""
    referral = ReferralFactory(user=self.user, referral_user=self.other_user)
    mock_check_ticket.return_value = False

    # 티켓이 부족한 사용자
    self.user.ticket_amount = 0
    self.user.save()

    data = {"referral_id": referral.id}

    self.client.force_authenticate(user=self.user)
    response = self.client.post(self.url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertIn("required_tickets", response.data["details"])
    self.assertIn("available_tickets", response.data["details"])

  @patch("api.v1.matchmakings.views.matchings.create_matching_api_view.MatchingService.create_matching_from_referral")
  @patch("api.v1.matchmakings.views.matchings.create_matching_api_view.MatchingService.check_ticket_availability")
  def test_create_matching_referral_not_found(self, mock_check_ticket, mock_create_matching):
    """존재하지 않는 referral_id로 매칭 생성 시 404 에러 테스트"""
    from api.v1.matchmakings.exceptions import ReferralNotFoundError

    mock_check_ticket.return_value = True
    mock_create_matching.side_effect = ReferralNotFoundError()

    data = {"referral_id": 99999}

    self.client.force_authenticate(user=self.user)
    response = self.client.post(self.url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

  def test_create_matching_unauthenticated(self):
    """인증되지 않은 사용자의 요청은 401 에러 테스트"""
    referral = ReferralFactory(user=self.user, referral_user=self.other_user)
    data = {"referral_id": referral.id}

    response = self.client.post(self.url, data, format="json")

    self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

  @patch("api.v1.matchmakings.views.matchings.create_matching_api_view.MatchingService.create_matching_from_referral")
  @patch("api.v1.matchmakings.views.matchings.create_matching_api_view.MatchingService.check_ticket_availability")
  def test_create_matching_with_exact_ticket_amount(self, mock_check_ticket, mock_create_matching):
    """정확한 티켓 수량으로 매칭 생성 테스트"""
    referral = ReferralFactory(user=self.user, referral_user=self.other_user)

    # 티켓을 정확히 MATCHING_TICKET_COST만큼만 보유
    self.user.ticket_amount = MATCHING_TICKET_COST
    self.user.save()

    mock_check_ticket.return_value = True
    # mock_matching은 referral을 그대로 반환 (이미 생성된 referral 재사용)
    mock_create_matching.return_value = referral

    data = {"referral_id": referral.id}

    self.client.force_authenticate(user=self.user)
    response = self.client.post(self.url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_201_CREATED)

  @patch("api.v1.matchmakings.views.matchings.create_matching_api_view.MatchingService.create_matching_from_referral")
  @patch("api.v1.matchmakings.views.matchings.create_matching_api_view.MatchingService.check_ticket_availability")
  def test_create_matching_validates_serializer(self, mock_check_ticket, mock_create_matching):
    """시리얼라이저 검증 테스트"""
    mock_check_ticket.return_value = True
    mock_matching = ReferralFactory(user=self.user, referral_user=self.other_user)
    mock_create_matching.return_value = mock_matching

    # 잘못된 데이터 타입
    data = {"referral_id": "not_an_integer"}

    self.client.force_authenticate(user=self.user)
    response = self.client.post(self.url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

  @patch("api.v1.matchmakings.views.matchings.create_matching_api_view.MatchingService.create_matching_from_referral")
  @patch("api.v1.matchmakings.views.matchings.create_matching_api_view.MatchingService.check_ticket_availability")
  def test_create_matching_deducts_tickets(self, mock_check_ticket, mock_create_matching):
    """매칭 생성 시 티켓이 차감되는지 테스트 (서비스 레벨에서 처리)"""
    referral = ReferralFactory(user=self.user, referral_user=self.other_user)

    mock_check_ticket.return_value = True
    # mock_matching은 referral을 그대로 반환 (이미 생성된 referral 재사용)
    mock_create_matching.return_value = referral

    data = {"referral_id": referral.id}

    self.client.force_authenticate(user=self.user)
    response = self.client.post(self.url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    # create_matching_from_referral이 MATCHING_TICKET_COST로 호출되었는지 확인
    mock_create_matching.assert_called_once_with(self.user, referral.id, MATCHING_TICKET_COST)

  def test_create_matching_method_not_allowed(self):
    """GET 등 허용되지 않는 메서드 테스트"""
    self.client.force_authenticate(user=self.user)
    response = self.client.get(self.url)

    self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
