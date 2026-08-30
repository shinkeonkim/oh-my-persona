from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from api.v1.matchmakings.services import MatchingQueryService
from matchmakings.models import Matching
from profiles.models import Gender, Profile

User = get_user_model()


class MatchingQueryServiceTest(TestCase):
  """MatchingQueryService 테스트"""

  def setUp(self):
    """테스트 데이터 설정"""
    # 사용자 생성
    self.user = User.objects.create_user(
        username="test_user",
        email="test@test.com",
        ticket_amount=100,
    )
    self.partner1 = User.objects.create_user(
        username="partner1",
        email="partner1@test.com",
        ticket_amount=50,
    )
    self.partner2 = User.objects.create_user(
        username="partner2",
        email="partner2@test.com",
        ticket_amount=50,
    )
    self.partner3 = User.objects.create_user(
        username="partner3",
        email="partner3@test.com",
        ticket_amount=50,
    )

    # 프로필 생성
    Profile.objects.create(user=self.user, gender=Gender.MALE)
    Profile.objects.create(user=self.partner1, gender=Gender.FEMALE)
    Profile.objects.create(user=self.partner2, gender=Gender.FEMALE)
    Profile.objects.create(user=self.partner3, gender=Gender.FEMALE)

  def test_get_sent_matchings_only_pending(self):
    """보낸 호감 목록이 진행 중인 것만 조회되는지 테스트"""
    # 진행 중인 매칭 생성
    pending_matching = Matching.objects.create(
        sender=self.user,
        receiver=self.partner1,
        ticket_amount=10,
        sent_at=timezone.now(),
    )

    # 수락된 매칭 생성
    Matching.objects.create(
        sender=self.user,
        receiver=self.partner2,
        ticket_amount=10,
        sent_at=timezone.now() - timedelta(days=2),
        received_at=timezone.now() - timedelta(days=1),
    )

    # 조회
    sent_matchings = MatchingQueryService.get_sent_matchings(self.user)

    # 진행 중인 것만 조회되는지 확인
    self.assertEqual(sent_matchings.count(), 1)
    self.assertEqual(sent_matchings.first().id, pending_matching.id)

  def test_get_sent_matchings_excludes_rejected(self):
    """보낸 호감 목록에 거절된 것은 제외되는지 테스트"""
    # 진행 중인 매칭 생성
    pending_matching = Matching.objects.create(
        sender=self.user,
        receiver=self.partner1,
        ticket_amount=10,
        sent_at=timezone.now(),
    )

    # 거절된 매칭 생성
    Matching.objects.create(
        sender=self.user,
        receiver=self.partner2,
        ticket_amount=10,
        sent_at=timezone.now() - timedelta(days=2),
        rejected_at=timezone.now() - timedelta(days=1),
    )

    # 조회
    sent_matchings = MatchingQueryService.get_sent_matchings(self.user)

    # 거절된 것은 제외되는지 확인
    self.assertEqual(sent_matchings.count(), 1)
    self.assertEqual(sent_matchings.first().id, pending_matching.id)

  def test_get_sent_matchings_excludes_expired(self):
    """보낸 호감 목록에 만료된 것은 제외되는지 테스트"""
    # 진행 중인 매칭 생성
    pending_matching = Matching.objects.create(
        sender=self.user,
        receiver=self.partner1,
        ticket_amount=10,
        sent_at=timezone.now(),
    )

    # 만료된 매칭 생성
    Matching.objects.create(
        sender=self.user,
        receiver=self.partner2,
        ticket_amount=10,
        sent_at=timezone.now() - timedelta(days=8),
        expired_at=timezone.now() - timedelta(days=1),
    )

    # 조회
    sent_matchings = MatchingQueryService.get_sent_matchings(self.user)

    # 만료된 것은 제외되는지 확인
    self.assertEqual(sent_matchings.count(), 1)
    self.assertEqual(sent_matchings.first().id, pending_matching.id)

  def test_get_sent_matchings_ordered_by_sent_at_desc(self):
    """보낸 호감 목록이 전송 일시 내림차순으로 정렬되는지 테스트"""
    # 여러 매칭 생성 (시간차를 두고)
    matching1 = Matching.objects.create(
        sender=self.user,
        receiver=self.partner1,
        ticket_amount=10,
        sent_at=timezone.now() - timedelta(days=3),
    )
    matching2 = Matching.objects.create(
        sender=self.user,
        receiver=self.partner2,
        ticket_amount=10,
        sent_at=timezone.now() - timedelta(days=1),
    )
    matching3 = Matching.objects.create(
        sender=self.user,
        receiver=self.partner3,
        ticket_amount=10,
        sent_at=timezone.now(),
    )

    # 조회
    sent_matchings = list(MatchingQueryService.get_sent_matchings(self.user))

    # 최신순으로 정렬되었는지 확인
    self.assertEqual(len(sent_matchings), 3)
    self.assertEqual(sent_matchings[0].id, matching3.id)
    self.assertEqual(sent_matchings[1].id, matching2.id)
    self.assertEqual(sent_matchings[2].id, matching1.id)

  def test_get_received_matchings_only_pending(self):
    """받은 호감 목록이 진행 중인 것만 조회되는지 테스트"""
    # 진행 중인 매칭 생성
    pending_matching = Matching.objects.create(
        sender=self.partner1,
        receiver=self.user,
        ticket_amount=10,
        sent_at=timezone.now(),
    )

    # 수락된 매칭 생성
    Matching.objects.create(
        sender=self.partner2,
        receiver=self.user,
        ticket_amount=10,
        sent_at=timezone.now() - timedelta(days=2),
        received_at=timezone.now() - timedelta(days=1),
    )

    # 조회
    received_matchings = MatchingQueryService.get_received_matchings(self.user)

    # 진행 중인 것만 조회되는지 확인
    self.assertEqual(received_matchings.count(), 1)
    self.assertEqual(received_matchings.first().id, pending_matching.id)

  def test_get_received_matchings_excludes_rejected(self):
    """받은 호감 목록에 거절된 것은 제외되는지 테스트"""
    # 진행 중인 매칭 생성
    pending_matching = Matching.objects.create(
        sender=self.partner1,
        receiver=self.user,
        ticket_amount=10,
        sent_at=timezone.now(),
    )

    # 거절된 매칭 생성
    Matching.objects.create(
        sender=self.partner2,
        receiver=self.user,
        ticket_amount=10,
        sent_at=timezone.now() - timedelta(days=2),
        rejected_at=timezone.now() - timedelta(days=1),
    )

    # 조회
    received_matchings = MatchingQueryService.get_received_matchings(self.user)

    # 거절된 것은 제외되는지 확인
    self.assertEqual(received_matchings.count(), 1)
    self.assertEqual(received_matchings.first().id, pending_matching.id)

  def test_get_received_matchings_excludes_expired(self):
    """받은 호감 목록에 만료된 것은 제외되는지 테스트"""
    # 진행 중인 매칭 생성
    pending_matching = Matching.objects.create(
        sender=self.partner1,
        receiver=self.user,
        ticket_amount=10,
        sent_at=timezone.now(),
    )

    # 만료된 매칭 생성
    Matching.objects.create(
        sender=self.partner2,
        receiver=self.user,
        ticket_amount=10,
        sent_at=timezone.now() - timedelta(days=8),
        expired_at=timezone.now() - timedelta(days=1),
    )

    # 조회
    received_matchings = MatchingQueryService.get_received_matchings(self.user)

    # 만료된 것은 제외되는지 확인
    self.assertEqual(received_matchings.count(), 1)
    self.assertEqual(received_matchings.first().id, pending_matching.id)

  def test_get_completed_matchings_only_accepted(self):
    """매칭 완료 목록이 수락된 것만 조회되는지 테스트"""
    # 수락된 매칭 생성
    accepted_matching = Matching.objects.create(
        sender=self.partner1,
        receiver=self.user,
        ticket_amount=10,
        sent_at=timezone.now() - timedelta(days=2),
        received_at=timezone.now() - timedelta(days=1),
    )

    # 진행 중인 매칭 생성
    Matching.objects.create(
        sender=self.partner2,
        receiver=self.user,
        ticket_amount=10,
        sent_at=timezone.now(),
    )

    # 조회
    completed_matchings = MatchingQueryService.get_completed_matchings(self.user)

    # 수락된 것만 조회되는지 확인
    self.assertEqual(completed_matchings.count(), 1)
    self.assertEqual(completed_matchings.first().id, accepted_matching.id)

  def test_get_completed_matchings_includes_both_sent_and_received(self):
    """매칭 완료 목록에 보낸/받은 것 모두 포함되는지 테스트"""
    # 보낸 매칭 중 수락된 것
    sent_accepted = Matching.objects.create(
        sender=self.user,
        receiver=self.partner1,
        ticket_amount=10,
        sent_at=timezone.now() - timedelta(days=2),
        received_at=timezone.now() - timedelta(days=1),
    )

    # 받은 매칭 중 수락된 것
    received_accepted = Matching.objects.create(
        sender=self.partner2,
        receiver=self.user,
        ticket_amount=10,
        sent_at=timezone.now() - timedelta(days=3),
        received_at=timezone.now() - timedelta(days=2),
    )

    # 조회
    completed_matchings = MatchingQueryService.get_completed_matchings(self.user)

    # 둘 다 포함되는지 확인
    self.assertEqual(completed_matchings.count(), 2)
    matching_ids = [m.id for m in completed_matchings]
    self.assertIn(sent_accepted.id, matching_ids)
    self.assertIn(received_accepted.id, matching_ids)

  def test_get_completed_matchings_ordered_by_received_at_desc(self):
    """매칭 완료 목록이 수락 일시 내림차순으로 정렬되는지 테스트"""
    # 여러 수락된 매칭 생성
    matching1 = Matching.objects.create(
        sender=self.partner1,
        receiver=self.user,
        ticket_amount=10,
        sent_at=timezone.now() - timedelta(days=5),
        received_at=timezone.now() - timedelta(days=3),
    )
    matching2 = Matching.objects.create(
        sender=self.partner2,
        receiver=self.user,
        ticket_amount=10,
        sent_at=timezone.now() - timedelta(days=3),
        received_at=timezone.now() - timedelta(days=1),
    )
    matching3 = Matching.objects.create(
        sender=self.partner3,
        receiver=self.user,
        ticket_amount=10,
        sent_at=timezone.now() - timedelta(days=2),
        received_at=timezone.now(),
    )

    # 조회
    completed_matchings = list(MatchingQueryService.get_completed_matchings(self.user))

    # 최신순으로 정렬되었는지 확인
    self.assertEqual(len(completed_matchings), 3)
    self.assertEqual(completed_matchings[0].id, matching3.id)
    self.assertEqual(completed_matchings[1].id, matching2.id)
    self.assertEqual(completed_matchings[2].id, matching1.id)

  def test_get_past_connections_includes_rejected(self):
    """지난 인연 목록에 거절된 것이 포함되는지 테스트"""
    # 거절된 매칭 생성
    rejected_matching = Matching.objects.create(
        sender=self.partner1,
        receiver=self.user,
        ticket_amount=10,
        sent_at=timezone.now() - timedelta(days=2),
        rejected_at=timezone.now() - timedelta(days=1),
    )

    # 조회
    past_connections = MatchingQueryService.get_past_connections(self.user)

    # 거절된 것이 포함되는지 확인
    self.assertEqual(past_connections.count(), 1)
    self.assertEqual(past_connections.first().id, rejected_matching.id)

  def test_get_past_connections_includes_expired(self):
    """지난 인연 목록에 만료된 것이 포함되는지 테스트"""
    # 만료된 매칭 생성
    expired_matching = Matching.objects.create(
        sender=self.user,
        receiver=self.partner1,
        ticket_amount=10,
        sent_at=timezone.now() - timedelta(days=8),
        expired_at=timezone.now() - timedelta(days=1),
    )

    # 조회
    past_connections = MatchingQueryService.get_past_connections(self.user)

    # 만료된 것이 포함되는지 확인
    self.assertEqual(past_connections.count(), 1)
    self.assertEqual(past_connections.first().id, expired_matching.id)

  def test_get_past_connections_excludes_pending_and_accepted(self):
    """지난 인연 목록에 진행 중/수락된 것은 제외되는지 테스트"""
    # 진행 중인 매칭
    Matching.objects.create(
        sender=self.user,
        receiver=self.partner1,
        ticket_amount=10,
        sent_at=timezone.now(),
    )

    # 수락된 매칭
    Matching.objects.create(
        sender=self.partner2,
        receiver=self.user,
        ticket_amount=10,
        sent_at=timezone.now() - timedelta(days=2),
        received_at=timezone.now() - timedelta(days=1),
    )

    # 거절된 매칭
    rejected_matching = Matching.objects.create(
        sender=self.partner3,
        receiver=self.user,
        ticket_amount=10,
        sent_at=timezone.now() - timedelta(days=3),
        rejected_at=timezone.now() - timedelta(days=2),
    )

    # 조회
    past_connections = MatchingQueryService.get_past_connections(self.user)

    # 거절된 것만 포함되는지 확인
    self.assertEqual(past_connections.count(), 1)
    self.assertEqual(past_connections.first().id, rejected_matching.id)

  def test_get_past_connections_includes_both_sent_and_received(self):
    """지난 인연 목록에 보낸/받은 것 모두 포함되는지 테스트"""
    # 보낸 매칭 중 거절된 것
    sent_rejected = Matching.objects.create(
        sender=self.user,
        receiver=self.partner1,
        ticket_amount=10,
        sent_at=timezone.now() - timedelta(days=2),
        rejected_at=timezone.now() - timedelta(days=1),
    )

    # 받은 매칭 중 만료된 것
    received_expired = Matching.objects.create(
        sender=self.partner2,
        receiver=self.user,
        ticket_amount=10,
        sent_at=timezone.now() - timedelta(days=8),
        expired_at=timezone.now() - timedelta(days=1),
    )

    # 조회
    past_connections = MatchingQueryService.get_past_connections(self.user)

    # 둘 다 포함되는지 확인
    self.assertEqual(past_connections.count(), 2)
    matching_ids = [m.id for m in past_connections]
    self.assertIn(sent_rejected.id, matching_ids)
    self.assertIn(received_expired.id, matching_ids)

  def test_get_past_connections_ordered_by_past_connection_at_desc(self):
    """지난 인연 목록이 종료 일시 내림차순으로 정렬되는지 테스트"""
    # 여러 거절/만료된 매칭 생성
    matching1 = Matching.objects.create(
        sender=self.partner1,
        receiver=self.user,
        ticket_amount=10,
        sent_at=timezone.now() - timedelta(days=5),
        rejected_at=timezone.now() - timedelta(days=3),
    )
    matching2 = Matching.objects.create(
        sender=self.partner2,
        receiver=self.user,
        ticket_amount=10,
        sent_at=timezone.now() - timedelta(days=10),
        expired_at=timezone.now() - timedelta(days=1),
    )
    matching3 = Matching.objects.create(
        sender=self.partner3,
        receiver=self.user,
        ticket_amount=10,
        sent_at=timezone.now() - timedelta(days=4),
        rejected_at=timezone.now() - timedelta(days=2),
    )

    # 조회
    past_connections = list(MatchingQueryService.get_past_connections(self.user))

    # 최신순으로 정렬되었는지 확인
    self.assertEqual(len(past_connections), 3)
    self.assertEqual(past_connections[0].id, matching2.id)  # 1일 전 만료
    self.assertEqual(past_connections[1].id, matching3.id)  # 2일 전 거절
    self.assertEqual(past_connections[2].id, matching1.id)  # 3일 전 거절

  def test_queries_select_related_profiles(self):
    """모든 쿼리가 프로필 정보를 select_related로 가져오는지 테스트"""
    # 매칭 생성
    Matching.objects.create(
        sender=self.user,
        receiver=self.partner1,
        ticket_amount=10,
        sent_at=timezone.now(),
    )

    # 쿼리 실행
    with self.assertNumQueries(1):
      sent_matchings = list(MatchingQueryService.get_sent_matchings(self.user))
      # 프로필 접근 시 추가 쿼리가 발생하지 않는지 확인
      for matching in sent_matchings:
        _ = matching.sender.profile
        _ = matching.receiver.profile

  def test_empty_results_when_no_matchings(self):
    """매칭이 없을 때 빈 결과를 반환하는지 테스트"""
    sent_matchings = MatchingQueryService.get_sent_matchings(self.user)
    received_matchings = MatchingQueryService.get_received_matchings(self.user)
    completed_matchings = MatchingQueryService.get_completed_matchings(self.user)
    past_connections = MatchingQueryService.get_past_connections(self.user)

    self.assertEqual(sent_matchings.count(), 0)
    self.assertEqual(received_matchings.count(), 0)
    self.assertEqual(completed_matchings.count(), 0)
    self.assertEqual(past_connections.count(), 0)

  def test_get_sent_matchings_does_not_include_received(self):
    """보낸 호감 목록에 받은 호감은 포함되지 않는지 테스트"""
    # 보낸 매칭
    sent_matching = Matching.objects.create(
        sender=self.user,
        receiver=self.partner1,
        ticket_amount=10,
        sent_at=timezone.now(),
    )

    # 받은 매칭
    Matching.objects.create(
        sender=self.partner2,
        receiver=self.user,
        ticket_amount=10,
        sent_at=timezone.now(),
    )

    # 조회
    sent_matchings = MatchingQueryService.get_sent_matchings(self.user)

    # 보낸 것만 포함되는지 확인
    self.assertEqual(sent_matchings.count(), 1)
    self.assertEqual(sent_matchings.first().id, sent_matching.id)

  def test_get_received_matchings_does_not_include_sent(self):
    """받은 호감 목록에 보낸 호감은 포함되지 않는지 테스트"""
    # 보낸 매칭
    Matching.objects.create(
        sender=self.user,
        receiver=self.partner1,
        ticket_amount=10,
        sent_at=timezone.now(),
    )

    # 받은 매칭
    received_matching = Matching.objects.create(
        sender=self.partner2,
        receiver=self.user,
        ticket_amount=10,
        sent_at=timezone.now(),
    )

    # 조회
    received_matchings = MatchingQueryService.get_received_matchings(self.user)

    # 받은 것만 포함되는지 확인
    self.assertEqual(received_matchings.count(), 1)
    self.assertEqual(received_matchings.first().id, received_matching.id)
