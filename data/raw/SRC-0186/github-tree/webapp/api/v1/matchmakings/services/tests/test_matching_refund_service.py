from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from api.v1.matchmakings.services import MatchingRefundService
from matchmakings.models import Matching
from profiles.models import Gender, Profile
from users.models import TicketLog, TicketLogCategory

User = get_user_model()


class MatchingRefundServiceTest(TestCase):
  """MatchingRefundService 테스트"""

  def setUp(self):
    """테스트 데이터 설정"""
    # 사용자 생성
    self.sender = User.objects.create_user(
      username="sender",
      email="sender@test.com",
      ticket_amount=200,
      used_ticket_amount=150,
    )
    self.receiver = User.objects.create_user(
      username="receiver",
      email="receiver@test.com",
      ticket_amount=100,
    )

    # 프로필 생성
    Profile.objects.create(user=self.sender, gender=Gender.MALE)
    Profile.objects.create(user=self.receiver, gender=Gender.FEMALE)

    self.ticket_cost = settings.MATCHING_TICKET_COST
    self.refund_amount = settings.MATCHING_REFUND_TICKET_AMOUNT

    # 매칭 생성
    self.matching = Matching.objects.create(
      sender=self.sender,
      receiver=self.receiver,
      ticket_amount=self.ticket_cost,
      sent_at=timezone.now(),
    )

  def test_refund_matching_ticket_success(self):
    """매칭 티켓 환불이 정상적으로 처리되는지 테스트"""
    initial_ticket_amount = self.sender.ticket_amount
    initial_used_ticket_amount = self.sender.used_ticket_amount

    # 환불 실행
    result = MatchingRefundService.refund_matching_ticket(self.matching)

    # 환불 성공 확인
    self.assertTrue(result)

    # 티켓 수량 확인
    self.sender.refresh_from_db()
    self.assertEqual(
      self.sender.ticket_amount,
      initial_ticket_amount + self.refund_amount,
    )
    self.assertEqual(
      self.sender.used_ticket_amount,
      initial_used_ticket_amount - self.refund_amount,
    )

    # 환불 로그 확인
    refund_log = TicketLog.objects.filter(
      user=self.sender,
      category=TicketLogCategory.REFUND,
      matching=self.matching,
    ).first()
    self.assertIsNotNone(refund_log)
    self.assertEqual(refund_log.amount, self.refund_amount)

  def test_prevent_duplicate_refund(self):
    """중복 환불이 방지되는지 테스트"""
    # 첫 번째 환불
    result1 = MatchingRefundService.refund_matching_ticket(self.matching)
    self.assertTrue(result1)

    self.sender.refresh_from_db()
    ticket_after_first_refund = self.sender.ticket_amount

    # 두 번째 환불 시도
    result2 = MatchingRefundService.refund_matching_ticket(self.matching)
    self.assertFalse(result2)

    # 티켓 수량이 변경되지 않았는지 확인
    self.sender.refresh_from_db()
    self.assertEqual(self.sender.ticket_amount, ticket_after_first_refund)

    # 환불 로그가 하나만 있는지 확인
    refund_logs = TicketLog.objects.filter(
      user=self.sender,
      category=TicketLogCategory.REFUND,
      matching=self.matching,
    )
    self.assertEqual(refund_logs.count(), 1)

  def test_refund_correct_amount(self):
    """정확한 금액이 환불되는지 테스트"""
    initial_ticket_amount = self.sender.ticket_amount
    initial_used_ticket_amount = self.sender.used_ticket_amount

    # 환불 실행
    MatchingRefundService.refund_matching_ticket(self.matching)

    # 정확한 금액이 환불되었는지 확인
    self.sender.refresh_from_db()
    expected_ticket_amount = initial_ticket_amount + self.refund_amount
    expected_used_ticket_amount = initial_used_ticket_amount - self.refund_amount

    self.assertEqual(self.sender.ticket_amount, expected_ticket_amount)
    self.assertEqual(self.sender.used_ticket_amount, expected_used_ticket_amount)

  def test_refund_only_to_sender(self):
    """환불이 발신자에게만 이루어지는지 테스트"""
    receiver_initial_ticket = self.receiver.ticket_amount

    # 환불 실행
    MatchingRefundService.refund_matching_ticket(self.matching)

    # 수신자의 티켓은 변경되지 않았는지 확인
    self.receiver.refresh_from_db()
    self.assertEqual(self.receiver.ticket_amount, receiver_initial_ticket)

    # 환불 로그가 발신자에게만 있는지 확인
    sender_refund_logs = TicketLog.objects.filter(
      user=self.sender,
      category=TicketLogCategory.REFUND,
      matching=self.matching,
    )
    receiver_refund_logs = TicketLog.objects.filter(
      user=self.receiver,
      category=TicketLogCategory.REFUND,
      matching=self.matching,
    )

    self.assertEqual(sender_refund_logs.count(), 1)
    self.assertEqual(receiver_refund_logs.count(), 0)

  def test_refund_with_insufficient_used_tickets(self):
    """사용 티켓이 부족할 때 환불 시도 시 에러 발생 테스트"""
    # used_ticket_amount를 환불 금액보다 적게 설정
    self.sender.used_ticket_amount = self.refund_amount - 1
    self.sender.save()

    # 환불 시도 시 에러 발생 확인
    with self.assertRaises(ValueError) as context:
      MatchingRefundService.refund_matching_ticket(self.matching)

    self.assertIn("환불 가능한 사용 티켓이 부족합니다", str(context.exception))

  def test_refund_transaction_atomicity(self):
    """환불 처리가 트랜잭션으로 안전하게 처리되는지 테스트"""
    initial_ticket_amount = self.sender.ticket_amount
    initial_used_ticket_amount = self.sender.used_ticket_amount

    # 환불 실행
    MatchingRefundService.refund_matching_ticket(self.matching)

    # 티켓 수량과 로그가 모두 일관되게 처리되었는지 확인
    self.sender.refresh_from_db()

    refund_log = TicketLog.objects.filter(
      user=self.sender,
      category=TicketLogCategory.REFUND,
      matching=self.matching,
    ).first()

    # 티켓 증가량과 로그의 금액이 일치하는지 확인
    ticket_increase = self.sender.ticket_amount - initial_ticket_amount
    used_ticket_decrease = initial_used_ticket_amount - self.sender.used_ticket_amount

    self.assertEqual(ticket_increase, refund_log.amount)
    self.assertEqual(used_ticket_decrease, refund_log.amount)
    self.assertEqual(ticket_increase, self.refund_amount)

  def test_refund_creates_proper_log_description(self):
    """환불 로그에 적절한 설명이 포함되는지 테스트"""
    # 환불 실행
    MatchingRefundService.refund_matching_ticket(self.matching)

    # 로그 확인
    refund_log = TicketLog.objects.filter(
      user=self.sender,
      category=TicketLogCategory.REFUND,
      matching=self.matching,
    ).first()

    # 설명에 매칭 ID가 포함되어 있는지 확인
    self.assertIsNotNone(refund_log.description)
    self.assertIn(str(self.matching.id), refund_log.description)
    self.assertIn("환불", refund_log.description)

  def test_refund_with_different_matching_instances(self):
    """여러 매칭에 대해 독립적으로 환불이 처리되는지 테스트"""
    # 다른 사용자와 매칭 생성
    another_receiver = User.objects.create_user(
      username="another_receiver",
      email="another_receiver@test.com",
      ticket_amount=100,
    )
    Profile.objects.create(user=another_receiver, gender=Gender.FEMALE)

    another_matching = Matching.objects.create(
      sender=self.sender,
      receiver=another_receiver,
      ticket_amount=self.ticket_cost,
      sent_at=timezone.now(),
    )

    initial_ticket_amount = self.sender.ticket_amount

    # 첫 번째 매칭 환불
    result1 = MatchingRefundService.refund_matching_ticket(self.matching)
    self.assertTrue(result1)

    self.sender.refresh_from_db()

    # 두 번째 매칭 환불
    result2 = MatchingRefundService.refund_matching_ticket(another_matching)
    self.assertTrue(result2)

    self.sender.refresh_from_db()

    # 두 번 환불되었는지 확인
    self.assertEqual(
      self.sender.ticket_amount,
      initial_ticket_amount + (self.refund_amount * 2),
    )

    # 각 매칭에 대한 환불 로그가 별도로 생성되었는지 확인
    refund_logs = TicketLog.objects.filter(
      user=self.sender,
      category=TicketLogCategory.REFUND,
    )
    self.assertEqual(refund_logs.count(), 2)

  def test_no_ticket_manipulation_vulnerability(self):
    """티켓 수량 조작의 위험이 없는지 테스트 (동시성 제어)"""
    initial_ticket_amount = self.sender.ticket_amount
    initial_used_ticket_amount = self.sender.used_ticket_amount

    # 환불 실행
    MatchingRefundService.refund_matching_ticket(self.matching)

    # 데이터베이스에서 직접 조회하여 확인
    sender_from_db = User.objects.get(pk=self.sender.pk)

    # 정확히 refund_amount만큼만 증가했는지 확인
    self.assertEqual(
      sender_from_db.ticket_amount,
      initial_ticket_amount + self.refund_amount,
    )
    self.assertEqual(
      sender_from_db.used_ticket_amount,
      initial_used_ticket_amount - self.refund_amount,
    )

    # 로그와 실제 티켓 수량이 일치하는지 확인
    refund_log = TicketLog.objects.filter(
      user=self.sender,
      category=TicketLogCategory.REFUND,
      matching=self.matching,
    ).first()

    self.assertEqual(refund_log.amount, self.refund_amount)

    # 티켓 총량이 보존되는지 확인 (발행된 티켓의 총량은 불변)
    total_before = initial_ticket_amount + initial_used_ticket_amount
    total_after = sender_from_db.ticket_amount + sender_from_db.used_ticket_amount
    self.assertEqual(total_before, total_after)
