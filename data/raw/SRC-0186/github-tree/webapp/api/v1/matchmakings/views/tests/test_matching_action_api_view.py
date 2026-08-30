from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from common.choices import Gender
from matchmakings.factories import MatchingFactory
from users.factories import UserFactory

User = get_user_model()


class MatchingActionAPIViewTest(APITestCase):
  """MatchingActionAPIView 테스트"""

  def setUp(self):
    """테스트 데이터 설정"""
    self.user = UserFactory(confirm_user=True, confirm_user__profile_gender=Gender.MALE)
    self.other_user = UserFactory(confirm_user=True, confirm_user__profile_gender=Gender.FEMALE)

  def _get_url(self, matching_id):
    """URL 생성 헬퍼 메서드"""
    return reverse("matching-action", kwargs={"matching_id": matching_id})

  @patch("api.v1.matchmakings.views.matchings.matching_action_api_view.MatchingService.process_matching_action")
  def test_matching_action_accept_success(self, mock_process_action):
    """호감 승인 성공 테스트"""
    matching = MatchingFactory(
        sender=self.other_user,
        receiver=self.user,
        sent_at=timezone.now(),
        ticket_amount=10,
    )

    mock_process_action.return_value = matching

    data = {"action": "accept"}
    url = self._get_url(matching.id)

    self.client.force_authenticate(user=self.user)
    response = self.client.patch(url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    mock_process_action.assert_called_once_with(matching, "accept")

  @patch("api.v1.matchmakings.views.matchings.matching_action_api_view.MatchingService.process_matching_action")
  def test_matching_action_reject_success(self, mock_process_action):
    """호감 거절 성공 테스트"""
    matching = MatchingFactory(
        sender=self.other_user,
        receiver=self.user,
        sent_at=timezone.now(),
        ticket_amount=10,
    )

    mock_process_action.return_value = matching

    data = {"action": "reject"}
    url = self._get_url(matching.id)

    self.client.force_authenticate(user=self.user)
    response = self.client.patch(url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    mock_process_action.assert_called_once_with(matching, "reject")

  def test_matching_action_invalid_action(self):
    """유효하지 않은 action 값 테스트"""
    matching = MatchingFactory(
        sender=self.other_user,
        receiver=self.user,
        sent_at=timezone.now(),
        ticket_amount=10,
    )

    data = {"action": "invalid_action"}
    url = self._get_url(matching.id)

    self.client.force_authenticate(user=self.user)
    response = self.client.patch(url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

  def test_matching_action_missing_action(self):
    """action 필드 누락 시 400 에러 테스트"""
    matching = MatchingFactory(
        sender=self.other_user,
        receiver=self.user,
        sent_at=timezone.now(),
        ticket_amount=10,
    )

    data = {}
    url = self._get_url(matching.id)

    self.client.force_authenticate(user=self.user)
    response = self.client.patch(url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

  def test_matching_action_not_found(self):
    """존재하지 않는 매칭에 대한 액션 시도 시 404 에러 테스트"""
    data = {"action": "accept"}
    url = self._get_url(99999)

    self.client.force_authenticate(user=self.user)
    response = self.client.patch(url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

  def test_matching_action_unauthenticated(self):
    """인증되지 않은 사용자의 요청은 401 에러 테스트"""
    matching = MatchingFactory(
        sender=self.other_user,
        receiver=self.user,
        sent_at=timezone.now(),
        ticket_amount=10,
    )

    data = {"action": "accept"}
    url = self._get_url(matching.id)

    response = self.client.patch(url, data, format="json")

    self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

  @patch("api.v1.matchmakings.views.matchings.matching_action_api_view.MatchingService.process_matching_action")
  def test_matching_action_updates_matching(self, mock_process_action):
    """매칭 액션이 매칭을 업데이트하는지 테스트"""
    matching = MatchingFactory(
        sender=self.other_user,
        receiver=self.user,
        sent_at=timezone.now(),
        ticket_amount=10,
    )

    # 수락 후 received_at이 설정된 매칭 반환
    updated_matching = matching
    updated_matching.received_at = timezone.now()
    mock_process_action.return_value = updated_matching

    data = {"action": "accept"}
    url = self._get_url(matching.id)

    self.client.force_authenticate(user=self.user)
    response = self.client.patch(url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["id"], matching.id)

  def test_matching_action_method_not_allowed(self):
    """PATCH 이외의 메서드는 허용되지 않음 테스트"""
    matching = MatchingFactory(
        sender=self.other_user,
        receiver=self.user,
        sent_at=timezone.now(),
        ticket_amount=10,
    )

    data = {"action": "accept"}
    url = self._get_url(matching.id)

    self.client.force_authenticate(user=self.user)

    # GET 요청
    response = self.client.get(url)
    self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # POST 요청
    response = self.client.post(url, data, format="json")
    self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

  @patch("api.v1.matchmakings.views.matchings.matching_action_api_view.MatchingService.process_matching_action")
  def test_matching_action_with_already_processed_matching(self, mock_process_action):
    """이미 처리된 매칭에 대한 액션 시도 테스트"""
    from api.v1.matchmakings.exceptions import MatchingValidationError

    matching = MatchingFactory(
        sender=self.other_user,
        receiver=self.user,
        sent_at=timezone.now(),
        received_at=timezone.now(),  # 이미 수락됨
        ticket_amount=10,
    )

    mock_process_action.side_effect = MatchingValidationError(message="Matching already processed")

    data = {"action": "accept"}
    url = self._get_url(matching.id)

    self.client.force_authenticate(user=self.user)
    response = self.client.patch(url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

  @patch("api.v1.matchmakings.views.matchings.matching_action_api_view.MatchingService.process_matching_action")
  def test_matching_action_calls_service_with_correct_params(self, mock_process_action):
    """서비스 메서드가 올바른 파라미터로 호출되는지 테스트"""
    matching = MatchingFactory(
        sender=self.other_user,
        receiver=self.user,
        sent_at=timezone.now(),
        ticket_amount=10,
    )

    mock_process_action.return_value = matching

    data = {"action": "reject"}
    url = self._get_url(matching.id)

    self.client.force_authenticate(user=self.user)
    response = self.client.patch(url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    # 서비스가 매칭 객체와 action으로 호출되었는지 확인
    call_args = mock_process_action.call_args
    self.assertEqual(call_args[0][0].id, matching.id)
    self.assertEqual(call_args[0][1], "reject")
