from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from api.v1.matchmakings.services import MatchingService

User = get_user_model()


class MatchingServiceTest(TestCase):
  """MatchingService 테스트 (Facade 패턴)"""

  def setUp(self):
    """테스트 데이터 설정"""
    self.user = User.objects.create_user(
        username="test_user",
        email="test@test.com",
        ticket_amount=100,
    )

  @patch("api.v1.matchmakings.services.matching_service.MatchingQueryService.get_sent_matchings")
  def test_get_sent_matchings(self, mock_get_sent):
    """보낸 호감 목록 조회가 MatchingQueryService로 위임되는지 테스트"""
    mock_result = Mock()
    mock_get_sent.return_value = mock_result

    result = MatchingService.get_sent_matchings(self.user)

    mock_get_sent.assert_called_once_with(self.user)
    self.assertEqual(result, mock_result)

  @patch("api.v1.matchmakings.services.matching_service.MatchingQueryService.get_received_matchings")
  def test_get_received_matchings(self, mock_get_received):
    """받은 호감 목록 조회가 MatchingQueryService로 위임되는지 테스트"""
    mock_result = Mock()
    mock_get_received.return_value = mock_result

    result = MatchingService.get_received_matchings(self.user)

    mock_get_received.assert_called_once_with(self.user)
    self.assertEqual(result, mock_result)

  @patch("api.v1.matchmakings.services.matching_service.MatchingQueryService.get_completed_matchings")
  def test_get_completed_matchings(self, mock_get_completed):
    """매칭 완료 목록 조회가 MatchingQueryService로 위임되는지 테스트"""
    mock_result = Mock()
    mock_get_completed.return_value = mock_result

    result = MatchingService.get_completed_matchings(self.user)

    mock_get_completed.assert_called_once_with(self.user)
    self.assertEqual(result, mock_result)

  @patch("api.v1.matchmakings.services.matching_service.MatchingQueryService.get_past_connections")
  def test_get_past_connections(self, mock_get_past):
    """지난 인연 목록 조회가 MatchingQueryService로 위임되는지 테스트"""
    mock_result = Mock()
    mock_get_past.return_value = mock_result

    result = MatchingService.get_past_connections(self.user)

    mock_get_past.assert_called_once_with(self.user)
    self.assertEqual(result, mock_result)

  @patch("api.v1.matchmakings.services.matching_service.MatchingActionService.process_matching_action")
  def test_process_matching_action(self, mock_process):
    """매칭 액션 처리가 MatchingActionService로 위임되는지 테스트"""
    mock_matching = Mock()
    mock_result = Mock()
    mock_process.return_value = mock_result
    action = "accept"

    result = MatchingService.process_matching_action(mock_matching, action)

    mock_process.assert_called_once_with(mock_matching, action)
    self.assertEqual(result, mock_result)

  @patch("api.v1.matchmakings.services.matching_service.MatchingCreationService.create_matching_from_referral")
  def test_create_matching_from_referral_without_ticket_amount(self, mock_create):
    """티켓 수량 없이 추천으로부터 매칭 생성이 MatchingCreationService로 위임되는지 테스트"""
    mock_result = Mock()
    mock_create.return_value = mock_result
    referral_id = 1

    result = MatchingService.create_matching_from_referral(self.user, referral_id)

    mock_create.assert_called_once_with(self.user, referral_id, None)
    self.assertEqual(result, mock_result)

  @patch("api.v1.matchmakings.services.matching_service.MatchingCreationService.create_matching_from_referral")
  def test_create_matching_from_referral_with_ticket_amount(self, mock_create):
    """티켓 수량과 함께 추천으로부터 매칭 생성이 MatchingCreationService로 위임되는지 테스트"""
    mock_result = Mock()
    mock_create.return_value = mock_result
    referral_id = 1
    ticket_amount = 15

    result = MatchingService.create_matching_from_referral(self.user, referral_id, ticket_amount)

    mock_create.assert_called_once_with(self.user, referral_id, ticket_amount)
    self.assertEqual(result, mock_result)

  @patch("api.v1.matchmakings.services.matching_service.MatchingCreationService.check_ticket_availability")
  def test_check_ticket_availability_without_amount(self, mock_check):
    """티켓 수량 없이 티켓 보유량 확인이 MatchingCreationService로 위임되는지 테스트"""
    mock_result = True
    mock_check.return_value = mock_result

    result = MatchingService.check_ticket_availability(self.user)

    mock_check.assert_called_once_with(self.user, None)
    self.assertEqual(result, mock_result)

  @patch("api.v1.matchmakings.services.matching_service.MatchingCreationService.check_ticket_availability")
  def test_check_ticket_availability_with_amount(self, mock_check):
    """티켓 수량과 함께 티켓 보유량 확인이 MatchingCreationService로 위임되는지 테스트"""
    mock_result = False
    mock_check.return_value = mock_result
    ticket_amount = 200

    result = MatchingService.check_ticket_availability(self.user, ticket_amount)

    mock_check.assert_called_once_with(self.user, ticket_amount)
    self.assertEqual(result, mock_result)

  @patch("api.v1.matchmakings.services.matching_service.MatchingCreationService.get_required_ticket_amount")
  def test_get_required_ticket_amount(self, mock_get_amount):
    """필요한 티켓 수량 조회가 MatchingCreationService로 위임되는지 테스트"""
    mock_result = 10
    mock_get_amount.return_value = mock_result

    result = MatchingService.get_required_ticket_amount()

    mock_get_amount.assert_called_once()
    self.assertEqual(result, mock_result)
