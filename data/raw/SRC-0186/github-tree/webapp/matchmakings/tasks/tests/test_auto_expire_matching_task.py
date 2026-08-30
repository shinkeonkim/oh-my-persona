from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from matchmakings.models import Matching
from matchmakings.tasks.auto_expire_matching_task import auto_expire_matching_task
from profiles.models import Gender, Profile
from users.models import TicketLog, TicketLogCategory

User = get_user_model()


class AutoExpireMatchingTaskTest(TestCase):
  """auto_expire_matching_task 테스트"""

  def setUp(self):
    """테스트 데이터 설정"""
    # 사용자 생성
    self.male_user = User.objects.create_user(
      username="male_user",
      email="male@test.com",
      ticket_amount=200,
      used_ticket_amount=150,
    )
    self.female_user = User.objects.create_user(
      username="female_user",
      email="female@test.com",
      ticket_amount=100,
    )

    # 프로필 생성
    Profile.objects.create(user=self.male_user, gender=Gender.MALE)
    Profile.objects.create(user=self.female_user, gender=Gender.FEMALE)

    self.ticket_cost = settings.MATCHING_TICKET_COST
    self.refund_amount = settings.MATCHING_REFUND_TICKET_AMOUNT
    self.auto_reject_days = settings.MATCHING_AUTO_REJECT_DAYS

  def test_expire_old_unaccepted_matchings(self):
    """1주일 지난 미수락 매칭이 자동으로 만료되는지 테스트"""
    # 1주일 지난 매칭 생성
    old_matching = Matching.objects.create(
      sender=self.male_user,
      receiver=self.female_user,
      ticket_amount=self.ticket_cost,
      sent_at=timezone.now() - timedelta(days=self.auto_reject_days + 1),
    )

    initial_ticket_amount = self.male_user.ticket_amount
    initial_used_ticket_amount = self.male_user.used_ticket_amount

    # 태스크 실행
    result = auto_expire_matching_task()

    # 매칭이 만료되었는지 확인
    old_matching.refresh_from_db()
    self.assertIsNotNone(old_matching.expired_at)
    self.assertIsNone(old_matching.received_at)
    self.assertIsNone(old_matching.rejected_at)

    # 티켓이 환불되었는지 확인
    self.male_user.refresh_from_db()
    self.assertEqual(
      self.male_user.ticket_amount,
      initial_ticket_amount + self.refund_amount,
    )
    self.assertEqual(
      self.male_user.used_ticket_amount,
      initial_used_ticket_amount - self.refund_amount,
    )

    # 환불 로그가 생성되었는지 확인
    refund_log = TicketLog.objects.filter(
      user=self.male_user,
      category=TicketLogCategory.REFUND,
      matching=old_matching,
    ).first()
    self.assertIsNotNone(refund_log)
    self.assertEqual(refund_log.amount, self.refund_amount)

    # 결과 메시지 확인
    self.assertIn("Auto-Expire 1 matchings", result)
    self.assertIn("refunded 1 tickets", result)

  def test_do_not_expire_recent_matchings(self):
    """최근 매칭은 만료되지 않는지 테스트"""
    # 최근 매칭 생성
    recent_matching = Matching.objects.create(
      sender=self.male_user,
      receiver=self.female_user,
      ticket_amount=self.ticket_cost,
      sent_at=timezone.now() - timedelta(days=self.auto_reject_days - 1),
    )

    # 태스크 실행
    result = auto_expire_matching_task()

    # 매칭이 만료되지 않았는지 확인
    recent_matching.refresh_from_db()
    self.assertIsNone(recent_matching.expired_at)

    # 결과 메시지 확인
    self.assertIn("Auto-Expire 0 matchings", result)

  def test_do_not_expire_already_received_matchings(self):
    """이미 수락된 매칭은 만료하지 않는지 테스트"""
    # 수락된 오래된 매칭 생성
    accepted_matching = Matching.objects.create(
      sender=self.male_user,
      receiver=self.female_user,
      ticket_amount=self.ticket_cost,
      sent_at=timezone.now() - timedelta(days=self.auto_reject_days + 1),
      received_at=timezone.now() - timedelta(days=1),
    )

    # 태스크 실행
    result = auto_expire_matching_task()

    # 매칭이 만료되지 않았는지 확인
    accepted_matching.refresh_from_db()
    self.assertIsNone(accepted_matching.expired_at)
    self.assertIsNotNone(accepted_matching.received_at)

    # 결과 메시지 확인
    self.assertIn("Auto-Expire 0 matchings", result)

  def test_do_not_expire_already_rejected_matchings(self):
    """이미 거절된 매칭은 만료하지 않는지 테스트"""
    # 거절된 오래된 매칭 생성
    rejected_matching = Matching.objects.create(
      sender=self.male_user,
      receiver=self.female_user,
      ticket_amount=self.ticket_cost,
      sent_at=timezone.now() - timedelta(days=self.auto_reject_days + 1),
      rejected_at=timezone.now() - timedelta(days=1),
    )

    # 태스크 실행
    result = auto_expire_matching_task()

    # 매칭이 만료되지 않았는지 확인
    rejected_matching.refresh_from_db()
    self.assertIsNone(rejected_matching.expired_at)
    self.assertIsNotNone(rejected_matching.rejected_at)

    # 결과 메시지 확인
    self.assertIn("Auto-Expire 0 matchings", result)

  def test_expire_multiple_matchings(self):
    """여러 매칭이 동시에 만료되는지 테스트"""
    # 여러 사용자 및 오래된 매칭 생성
    another_female = User.objects.create_user(
      username="another_female",
      email="another_female@test.com",
      ticket_amount=100,
    )
    Profile.objects.create(user=another_female, gender=Gender.FEMALE)

    old_matching1 = Matching.objects.create(
      sender=self.male_user,
      receiver=self.female_user,
      ticket_amount=self.ticket_cost,
      sent_at=timezone.now() - timedelta(days=self.auto_reject_days + 1),
    )

    old_matching2 = Matching.objects.create(
      sender=self.male_user,
      receiver=another_female,
      ticket_amount=self.ticket_cost,
      sent_at=timezone.now() - timedelta(days=self.auto_reject_days + 2),
    )

    initial_ticket_amount = self.male_user.ticket_amount

    # 태스크 실행
    result = auto_expire_matching_task()

    # 두 매칭 모두 만료되었는지 확인
    old_matching1.refresh_from_db()
    old_matching2.refresh_from_db()
    self.assertIsNotNone(old_matching1.expired_at)
    self.assertIsNotNone(old_matching2.expired_at)

    # 티켓이 두 번 환불되었는지 확인
    self.male_user.refresh_from_db()
    self.assertEqual(
      self.male_user.ticket_amount,
      initial_ticket_amount + (self.refund_amount * 2),
    )

    # 결과 메시지 확인
    self.assertIn("Auto-Expire 2 matchings", result)
    self.assertIn("refunded 2 tickets", result)

  def test_continue_on_individual_matching_error(self):
    """개별 매칭 처리 중 에러가 발생해도 다른 매칭은 계속 처리되는지 테스트"""
    # 오래된 매칭 2개 생성
    another_female = User.objects.create_user(
      username="another_female",
      email="another_female@test.com",
      ticket_amount=100,
    )
    Profile.objects.create(user=another_female, gender=Gender.FEMALE)

    old_matching1 = Matching.objects.create(
      sender=self.male_user,
      receiver=self.female_user,
      ticket_amount=self.ticket_cost,
      sent_at=timezone.now() - timedelta(days=self.auto_reject_days + 1),
    )

    # 두 번째 매칭은 이미 환불된 상태로 설정 (환불 로그만 생성)
    old_matching2 = Matching.objects.create(
      sender=self.male_user,
      receiver=another_female,
      ticket_amount=self.ticket_cost,
      sent_at=timezone.now() - timedelta(days=self.auto_reject_days + 2),
    )
    # 이미 환불된 것처럼 로그 생성
    TicketLog.objects.create(
      user=self.male_user,
      amount=self.refund_amount,
      category=TicketLogCategory.REFUND,
      matching=old_matching2,
      description="Already refunded",
    )

    # 태스크 실행
    result = auto_expire_matching_task()

    # 두 매칭 모두 만료되었는지 확인
    old_matching1.refresh_from_db()
    old_matching2.refresh_from_db()
    self.assertIsNotNone(old_matching1.expired_at)
    self.assertIsNotNone(old_matching2.expired_at)

    # 첫 번째만 환불되고 두 번째는 환불되지 않았는지 확인
    self.assertIn("Auto-Expire 2 matchings", result)
    self.assertIn("refunded 1 tickets", result)

  def test_task_with_no_expired_matchings(self):
    """만료 대상 매칭이 없을 때 태스크가 정상적으로 실행되는지 테스트"""
    # 최근 매칭만 생성
    Matching.objects.create(
      sender=self.male_user,
      receiver=self.female_user,
      ticket_amount=self.ticket_cost,
      sent_at=timezone.now() - timedelta(days=1),
    )

    # 태스크 실행
    result = auto_expire_matching_task()

    # 결과 메시지 확인
    self.assertIn("Auto-Expire 0 matchings", result)
    self.assertIn("refunded 0 tickets", result)
