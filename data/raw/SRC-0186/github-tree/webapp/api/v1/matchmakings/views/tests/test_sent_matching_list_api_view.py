from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from common.choices import Gender
from matchmakings.factories import MatchingFactory
from users.factories import UserFactory

User = get_user_model()


class SentMatchingListAPIViewTest(APITestCase):
  """SentMatchingListAPIView 테스트"""

  def setUp(self):
    """테스트 데이터 설정"""
    self.user = UserFactory(confirm_user=True, confirm_user__profile_gender=Gender.MALE)
    self.other_user = UserFactory(confirm_user=True, confirm_user__profile_gender=Gender.FEMALE)
    self.url = reverse("matching-sent-list")

  def test_get_sent_matchings_success(self):
    """보낸 호감 목록 조회 성공 테스트"""
    matching = MatchingFactory(
        sender=self.user,
        receiver=self.other_user,
        sent_at=timezone.now(),
        ticket_amount=10,
    )

    self.client.force_authenticate(user=self.user)
    response = self.client.get(self.url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["count"], 1)
    self.assertEqual(response.data["results"][0]["id"], matching.id)

  def test_get_sent_matchings_multiple(self):
    """여러 개의 보낸 호감 목록 조회 테스트"""
    user2 = UserFactory(confirm_user=True, confirm_user__profile_gender=Gender.FEMALE)
    user3 = UserFactory(confirm_user=True, confirm_user__profile_gender=Gender.FEMALE)

    matching1 = MatchingFactory(
        sender=self.user,
        receiver=user2,
        sent_at=timezone.now(),
        ticket_amount=10,
    )
    matching2 = MatchingFactory(
        sender=self.user,
        receiver=user3,
        sent_at=timezone.now(),
        ticket_amount=10,
    )

    self.client.force_authenticate(user=self.user)
    response = self.client.get(self.url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["count"], 2)
    result_ids = [item["id"] for item in response.data["results"]]
    self.assertIn(matching1.id, result_ids)
    self.assertIn(matching2.id, result_ids)

  def test_get_sent_matchings_excludes_received(self):
    """받은 호감은 제외되는지 테스트"""
    # 보낸 호감
    sent_matching = MatchingFactory(
        sender=self.user,
        receiver=self.other_user,
        sent_at=timezone.now(),
        ticket_amount=10,
    )

    # 받은 호감 (제외되어야 함)
    MatchingFactory(
        sender=self.other_user,
        receiver=self.user,
        sent_at=timezone.now(),
        ticket_amount=10,
    )

    self.client.force_authenticate(user=self.user)
    response = self.client.get(self.url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["count"], 1)
    self.assertEqual(response.data["results"][0]["id"], sent_matching.id)

  def test_get_sent_matchings_excludes_accepted(self):
    """수락된 매칭은 제외되는지 테스트"""
    # 대기 중인 보낸 호감
    pending_matching = MatchingFactory(
        sender=self.user,
        receiver=self.other_user,
        sent_at=timezone.now(),
        ticket_amount=10,
    )

    # 수락된 매칭 (제외되어야 함)
    MatchingFactory(
        sender=self.user,
        receiver=UserFactory(confirm_user=True, confirm_user__profile_gender=Gender.FEMALE),
        sent_at=timezone.now(),
        received_at=timezone.now(),
        ticket_amount=10,
    )

    self.client.force_authenticate(user=self.user)
    response = self.client.get(self.url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["count"], 1)
    self.assertEqual(response.data["results"][0]["id"], pending_matching.id)

  def test_get_sent_matchings_excludes_rejected(self):
    """거절된 매칭은 제외되는지 테스트"""
    # 대기 중인 보낸 호감
    pending_matching = MatchingFactory(
        sender=self.user,
        receiver=self.other_user,
        sent_at=timezone.now(),
        ticket_amount=10,
    )

    # 거절된 매칭 (제외되어야 함)
    other_receiver = UserFactory(confirm_user=True, confirm_user__profile_gender=Gender.FEMALE)
    MatchingFactory(
        sender=self.user,
        receiver=other_receiver,
        sent_at=timezone.now(),
        rejected_at=timezone.now(),
        ticket_amount=10,
    )

    self.client.force_authenticate(user=self.user)
    response = self.client.get(self.url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["count"], 1)
    self.assertEqual(response.data["results"][0]["id"], pending_matching.id)

  def test_get_sent_matchings_excludes_expired(self):
    """만료된 매칭은 제외되는지 테스트"""
    # 대기 중인 보낸 호감
    pending_matching = MatchingFactory(
        sender=self.user,
        receiver=self.other_user,
        sent_at=timezone.now(),
        ticket_amount=10,
    )

    # 만료된 매칭 (제외되어야 함)
    MatchingFactory(
        sender=self.user,
        receiver=UserFactory(confirm_user=True, confirm_user__profile_gender=Gender.FEMALE),
        sent_at=timezone.now(),
        expired_at=timezone.now(),
        ticket_amount=10,
    )

    self.client.force_authenticate(user=self.user)
    response = self.client.get(self.url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["count"], 1)
    self.assertEqual(response.data["results"][0]["id"], pending_matching.id)

  def test_get_sent_matchings_empty(self):
    """보낸 호감이 없을 때 빈 목록 반환 테스트"""
    self.client.force_authenticate(user=self.user)
    response = self.client.get(self.url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["count"], 0)
    self.assertEqual(len(response.data["results"]), 0)

  def test_get_sent_matchings_unauthenticated(self):
    """인증되지 않은 사용자의 요청은 401 또는 403 에러 테스트"""
    response = self.client.get(self.url)

    self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

  def test_get_sent_matchings_pagination(self):
    """페이지네이션 동작 테스트"""
    # 여러 개의 보낸 호감 생성
    for i in range(15):
      user = UserFactory(confirm_user=True, confirm_user__profile_gender=Gender.FEMALE)
      MatchingFactory(
          sender=self.user,
          receiver=user,
          sent_at=timezone.now(),
          ticket_amount=10,
      )

    self.client.force_authenticate(user=self.user)
    response = self.client.get(self.url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["count"], 15)
    self.assertLessEqual(len(response.data["results"]), 15)

  def test_get_sent_matchings_only_pending(self):
    """received_at과 rejected_at이 모두 NULL인 매칭만 조회되는지 테스트"""
    # 대기 중인 보낸 호감
    pending_matching = MatchingFactory(
        sender=self.user,
        receiver=self.other_user,
        sent_at=timezone.now(),
        ticket_amount=10,
    )

    self.client.force_authenticate(user=self.user)
    response = self.client.get(self.url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["count"], 1)
    result = response.data["results"][0]
    self.assertEqual(result["id"], pending_matching.id)
    self.assertIsNone(result.get("received_at"))
    self.assertIsNone(result.get("rejected_at"))

  def test_get_sent_matchings_only_user_related(self):
    """현재 사용자가 보낸 호감만 조회되는지 테스트"""
    another_user = UserFactory(confirm_user=True, confirm_user__profile_gender=Gender.FEMALE)
    another_user2 = UserFactory(confirm_user=True, confirm_user__profile_gender=Gender.MALE)

    # 현재 사용자가 보낸 호감
    my_matching = MatchingFactory(
        sender=self.user,
        receiver=self.other_user,
        sent_at=timezone.now(),
        ticket_amount=10,
    )

    # 다른 사용자가 보낸 호감 (조회되면 안됨)
    MatchingFactory(
        sender=another_user,
        receiver=another_user2,
        sent_at=timezone.now(),
        ticket_amount=10,
    )

    self.client.force_authenticate(user=self.user)
    response = self.client.get(self.url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["count"], 1)
    self.assertEqual(response.data["results"][0]["id"], my_matching.id)
