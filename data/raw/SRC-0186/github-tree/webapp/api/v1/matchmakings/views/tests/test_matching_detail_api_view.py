from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from common.choices import Gender
from matchmakings.factories import MatchingFactory
from users.factories import UserFactory

User = get_user_model()


class MatchingDetailAPIViewTest(APITestCase):
  """MatchingDetailAPIView 테스트"""

  def setUp(self):
    """테스트 데이터 설정"""
    self.user = UserFactory(confirm_user=True, confirm_user__profile_gender=Gender.MALE)
    self.other_user = UserFactory(confirm_user=True, confirm_user__profile_gender=Gender.FEMALE)

  def _get_url(self, matching_id):
    """URL 생성 헬퍼 메서드"""
    return reverse("matching-detail", kwargs={"matching_id": matching_id})

  def test_get_matching_detail_as_sender(self):
    """보낸 매칭 상세 조회 성공 테스트"""
    matching = MatchingFactory(
      sender=self.user,
      receiver=self.other_user,
      sent_at=timezone.now(),
      ticket_amount=10,
    )

    url = self._get_url(matching.id)

    self.client.force_authenticate(user=self.user)
    response = self.client.get(url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["id"], matching.id)

  def test_get_matching_detail_as_receiver(self):
    """받은 매칭 상세 조회 성공 테스트"""
    matching = MatchingFactory(
      sender=self.other_user,
      receiver=self.user,
      sent_at=timezone.now(),
      ticket_amount=10,
    )

    url = self._get_url(matching.id)

    self.client.force_authenticate(user=self.user)
    response = self.client.get(url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["id"], matching.id)

  def test_get_matching_detail_not_found(self):
    """존재하지 않는 매칭 조회 시 404 에러 테스트"""
    url = self._get_url(99999)

    self.client.force_authenticate(user=self.user)
    response = self.client.get(url)

    self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

  def test_get_matching_detail_unauthenticated(self):
    """인증되지 않은 사용자의 요청은 401 에러 테스트"""
    matching = MatchingFactory(
      sender=self.user,
      receiver=self.other_user,
      sent_at=timezone.now(),
      ticket_amount=10,
    )

    url = self._get_url(matching.id)

    response = self.client.get(url)

    self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

  def test_get_matching_detail_access_denied(self):
    """본인의 매칭이 아닌 경우 접근 거부 테스트"""
    another_user = UserFactory(confirm_user=True, confirm_user__profile_gender=Gender.FEMALE)
    another_user2 = UserFactory(confirm_user=True, confirm_user__profile_gender=Gender.MALE)

    # 다른 사용자들 간의 매칭
    matching = MatchingFactory(
      sender=another_user,
      receiver=another_user2,
      sent_at=timezone.now(),
      ticket_amount=10,
    )

    url = self._get_url(matching.id)

    self.client.force_authenticate(user=self.user)
    response = self.client.get(url)

    # 403 또는 404 (권한에 따라 다를 수 있음)
    self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

  def test_get_matching_detail_with_completed_matching(self):
    """완료된 매칭(수락됨) 상세 조회 테스트"""
    matching = MatchingFactory(
      sender=self.user,
      receiver=self.other_user,
      sent_at=timezone.now(),
      received_at=timezone.now(),
      ticket_amount=10,
    )

    url = self._get_url(matching.id)

    self.client.force_authenticate(user=self.user)
    response = self.client.get(url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["id"], matching.id)
    self.assertIsNotNone(response.data["received_at"])

  def test_get_matching_detail_with_rejected_matching(self):
    """거절된 매칭 상세 조회 테스트"""
    matching = MatchingFactory(
      sender=self.user,
      receiver=self.other_user,
      sent_at=timezone.now(),
      rejected_at=timezone.now(),
      ticket_amount=10,
    )

    url = self._get_url(matching.id)

    self.client.force_authenticate(user=self.user)
    response = self.client.get(url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data["id"], matching.id)
    self.assertIsNotNone(response.data["rejected_at"])

  def test_get_matching_detail_returns_sender_profile(self):
    """매칭 상세에 sender 프로필 정보가 포함되는지 테스트"""
    matching = MatchingFactory(
      sender=self.user,
      receiver=self.other_user,
      sent_at=timezone.now(),
      ticket_amount=10,
    )

    url = self._get_url(matching.id)

    self.client.force_authenticate(user=self.user)
    response = self.client.get(url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    # sender 정보가 응답에 포함되어야 함
    self.assertIn("sender", response.data)

  def test_get_matching_detail_returns_receiver_profile(self):
    """매칭 상세에 receiver 프로필 정보가 포함되는지 테스트"""
    matching = MatchingFactory(
      sender=self.user,
      receiver=self.other_user,
      sent_at=timezone.now(),
      ticket_amount=10,
    )

    url = self._get_url(matching.id)

    self.client.force_authenticate(user=self.user)
    response = self.client.get(url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    # receiver 정보가 응답에 포함되어야 함
    self.assertIn("receiver", response.data)

  def test_get_matching_detail_method_not_allowed(self):
    """GET 이외의 메서드는 허용되지 않음 테스트"""
    matching = MatchingFactory(
      sender=self.user,
      receiver=self.other_user,
      sent_at=timezone.now(),
      ticket_amount=10,
    )

    url = self._get_url(matching.id)

    self.client.force_authenticate(user=self.user)

    # POST 요청
    response = self.client.post(url, {}, format="json")
    self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # DELETE 요청
    response = self.client.delete(url)
    self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

  def test_get_matching_detail_with_related_data(self):
    """매칭 상세 조회 시 select_related로 관련 데이터가 함께 조회되는지 테스트"""
    matching = MatchingFactory(
      sender=self.user,
      receiver=self.other_user,
      sent_at=timezone.now(),
      ticket_amount=10,
    )

    url = self._get_url(matching.id)

    self.client.force_authenticate(user=self.user)

    # 쿼리 수 확인 (select_related 동작 검증)
    # 실제 쿼리: 1(main) + 2(job/job_category for sender) + 2(job/job_category for receiver)
    # + 2(profile representative_image/identity_verification for sender)
    # + 2(identity_verification) + 2(saju_profile) + 2(referral 관련) = 11
    with self.assertNumQueries(13):
      response = self.client.get(url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
