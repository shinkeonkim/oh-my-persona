from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from common.choices import Gender
from matchmakings.factories import MatchingFactory
from users.factories import UserFactory

User = get_user_model()


class PastConnectionListAPIViewTest(APITestCase):
  """PastConnectionListAPIView 테스트"""

  def setUp(self):
    """테스트 데이터 설정"""
    self.user = UserFactory(confirm_user=True, confirm_user__profile_gender=Gender.MALE)
    self.other_user = UserFactory(confirm_user=True, confirm_user__profile_gender=Gender.FEMALE)
    self.url = reverse("matching-past-list")

  def test_get_past_connections_with_rejected(self):
    """거절된 매칭이 지난 인연 목록에 포함되는지 테스트"""
    matching = MatchingFactory(
        sender=self.user,
        receiver=self.other_user,
        sent_at=timezone.now(),
        rejected_at=timezone.now(),
        ticket_amount=10,
    )

    self.client.force_authenticate(user=self.user)
    response = self.client.get(self.url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["count"], 1)
    self.assertEqual(response.data["results"][0]["id"], matching.id)

  def test_get_past_connections_excludes_completed(self):
    """완료된 매칭(수락됨)은 지난 인연에서 제외되는지 테스트"""
    # 거절된 매칭
    rejected_matching = MatchingFactory(
        sender=self.user,
        receiver=self.other_user,
        sent_at=timezone.now(),
        rejected_at=timezone.now(),
        ticket_amount=10,
    )

    # 완료된 매칭 (제외되어야 함)
    MatchingFactory(
        sender=self.user,
        receiver=UserFactory(confirm_user__profile_gender=Gender.FEMALE),
        sent_at=timezone.now(),
        received_at=timezone.now(),
        ticket_amount=10,
    )

    self.client.force_authenticate(user=self.user)
    response = self.client.get(self.url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["count"], 1)
    self.assertEqual(response.data["results"][0]["id"], rejected_matching.id)

  def test_get_past_connections_excludes_pending(self):
    """대기 중인 매칭은 지난 인연에서 제외되는지 테스트"""
    # 거절된 매칭
    rejected_matching = MatchingFactory(
        sender=self.user,
        receiver=self.other_user,
        sent_at=timezone.now(),
        rejected_at=timezone.now(),
        ticket_amount=10,
    )

    # 대기 중인 매칭 (제외되어야 함)
    MatchingFactory(
        sender=self.user,
        receiver=UserFactory(confirm_user__profile_gender=Gender.FEMALE),
        sent_at=timezone.now(),
        ticket_amount=10,
    )

    self.client.force_authenticate(user=self.user)
    response = self.client.get(self.url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["count"], 1)
    self.assertEqual(response.data["results"][0]["id"], rejected_matching.id)

  def test_get_past_connections_as_sender_and_receiver(self):
    """보낸 호감과 받은 호감 모두 지난 인연에 포함되는지 테스트"""
    user2 = UserFactory(confirm_user=True, confirm_user__profile_gender=Gender.FEMALE)
    user3 = UserFactory(confirm_user=True, confirm_user__profile_gender=Gender.FEMALE)

    # 보낸 호감 - 거절됨
    sent_matching = MatchingFactory(
        sender=self.user,
        receiver=user2,
        sent_at=timezone.now(),
        rejected_at=timezone.now(),
        ticket_amount=10,
    )

    # 받은 호감 - 거절함
    received_matching = MatchingFactory(
        sender=user3,
        receiver=self.user,
        sent_at=timezone.now(),
        rejected_at=timezone.now(),
        ticket_amount=10,
    )

    self.client.force_authenticate(user=self.user)
    response = self.client.get(self.url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["count"], 2)
    result_ids = [item["id"] for item in response.data["results"]]
    self.assertIn(sent_matching.id, result_ids)
    self.assertIn(received_matching.id, result_ids)

  def test_get_past_connections_empty(self):
    """지난 인연이 없을 때 빈 목록 반환 테스트"""
    self.client.force_authenticate(user=self.user)
    response = self.client.get(self.url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["count"], 0)
    self.assertEqual(len(response.data["results"]), 0)

  def test_get_past_connections_unauthenticated(self):
    """인증되지 않은 사용자의 요청은 401 또는 403 에러 테스트"""
    response = self.client.get(self.url)

    self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

  def test_get_past_connections_pagination(self):
    """페이지네이션 동작 테스트"""
    # 여러 개의 지난 인연 생성
    for i in range(15):
      user = UserFactory(confirm_user=True, confirm_user__profile_gender=Gender.FEMALE)
      MatchingFactory(
          sender=self.user,
          receiver=user,
          sent_at=timezone.now(),
          rejected_at=timezone.now(),
          ticket_amount=10,
      )

    self.client.force_authenticate(user=self.user)
    response = self.client.get(self.url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["count"], 15)
    self.assertLessEqual(len(response.data["results"]), 15)

  def test_get_past_connections_only_user_related(self):
    """현재 사용자와 관련된 지난 인연만 조회되는지 테스트"""
    another_user = UserFactory(confirm_user=True, confirm_user__profile_gender=Gender.FEMALE)
    another_user2 = UserFactory(confirm_user=True, confirm_user__profile_gender=Gender.MALE)

    # 현재 사용자의 지난 인연
    my_matching = MatchingFactory(
        sender=self.user,
        receiver=self.other_user,
        sent_at=timezone.now(),
        rejected_at=timezone.now(),
        ticket_amount=10,
    )

    # 다른 사용자의 지난 인연 (조회되면 안됨)
    MatchingFactory(
        sender=another_user,
        receiver=another_user2,
        sent_at=timezone.now(),
        rejected_at=timezone.now(),
        ticket_amount=10,
    )

    self.client.force_authenticate(user=self.user)
    response = self.client.get(self.url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["count"], 1)
    self.assertEqual(response.data["results"][0]["id"], my_matching.id)

  def test_get_past_connections_with_expired_matching(self):
    """만료된 매칭(expired_at 설정됨)이 지난 인연에 포함되는지 테스트"""
    # 만료된 매칭
    expired_matching = MatchingFactory(
        sender=self.user,
        receiver=self.other_user,
        sent_at=timezone.now(),
        expired_at=timezone.now(),
        ticket_amount=10,
    )

    self.client.force_authenticate(user=self.user)
    response = self.client.get(self.url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["count"], 1)
    self.assertEqual(response.data["results"][0]["id"], expired_matching.id)
