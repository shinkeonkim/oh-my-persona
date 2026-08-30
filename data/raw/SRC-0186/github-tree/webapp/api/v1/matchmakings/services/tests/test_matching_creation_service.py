from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from api.v1.matchmakings.exceptions import ReferralNotFoundError
from api.v1.matchmakings.services import MatchingCreationService
from common.exceptions.custom_exceptions import ValidationError
from matchmakings.models import Matching, Referral
from profiles.models import Gender, Profile
from users.models import TicketLog, TicketLogCategory

User = get_user_model()


class MatchingCreationServiceTest(TestCase):
  """MatchingCreationService 테스트"""

  def setUp(self):
    """테스트 데이터 설정"""
    # 사용자 생성
    self.sender = User.objects.create_user(
      username="sender",
      email="sender@test.com",
      ticket_amount=300,
      used_ticket_amount=0,
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

    # 추천 생성
    self.referral = Referral.objects.create(
      user=self.sender,
      referral_user=self.receiver,
      referred_at=timezone.now(),
      referred_algorithm="TestAlgorithm",
    )

  def test_create_matching_from_referral_success(self):
    """추천으로부터 매칭 생성이 정상적으로 처리되는지 테스트"""
    initial_ticket_amount = self.sender.ticket_amount

    # 매칭 생성
    matching = MatchingCreationService.create_matching_from_referral(self.sender, self.referral.id)

    # 매칭이 생성되었는지 확인
    self.assertIsNotNone(matching)
    self.assertEqual(matching.sender, self.sender)
    self.assertEqual(matching.receiver, self.receiver)
    self.assertEqual(matching.ticket_amount, self.ticket_cost)
    self.assertEqual(matching.referral, self.referral)
    self.assertIsNotNone(matching.sent_at)

    # 티켓이 차감되었는지 확인
    self.sender.refresh_from_db()
    self.assertEqual(
      self.sender.ticket_amount,
      initial_ticket_amount - self.ticket_cost,
    )
    self.assertEqual(self.sender.used_ticket_amount, self.ticket_cost)

    # 티켓 사용 로그가 생성되었는지 확인
    ticket_log = TicketLog.objects.filter(
      user=self.sender,
      category=TicketLogCategory.USE,
      matching=matching,
    ).first()
    self.assertIsNotNone(ticket_log)
    self.assertEqual(ticket_log.amount, self.ticket_cost)

  def test_create_matching_with_custom_ticket_amount(self):
    """커스텀 티켓 수량으로 매칭 생성이 가능한지 테스트"""
    custom_amount = 75
    initial_ticket_amount = self.sender.ticket_amount

    # 커스텀 티켓 수량으로 매칭 생성
    matching = MatchingCreationService.create_matching_from_referral(self.sender,
                                                                     self.referral.id,
                                                                     ticket_amount=custom_amount)

    # 커스텀 수량이 적용되었는지 확인
    self.assertEqual(matching.ticket_amount, custom_amount)

    # 커스텀 수량만큼 티켓이 차감되었는지 확인
    self.sender.refresh_from_db()
    self.assertEqual(
      self.sender.ticket_amount,
      initial_ticket_amount - custom_amount,
    )

  def test_create_matching_with_insufficient_tickets(self):
    """티켓이 부족할 때 매칭 생성 실패 테스트"""
    # 티켓을 부족하게 설정
    self.sender.ticket_amount = self.ticket_cost - 1
    self.sender.save()

    # 매칭 생성 시도
    with self.assertRaises(ValueError) as context:
      MatchingCreationService.create_matching_from_referral(self.sender, self.referral.id)

    self.assertIn("사용 가능한 티켓이 부족합니다", str(context.exception))

    # 매칭이 생성되지 않았는지 확인
    matching_count = Matching.objects.filter(sender=self.sender).count()
    self.assertEqual(matching_count, 0)

  def test_create_matching_with_nonexistent_referral(self):
    """존재하지 않는 추천으로 매칭 생성 시 에러 발생 테스트"""
    nonexistent_referral_id = 99999

    with self.assertRaises(ReferralNotFoundError):
      MatchingCreationService.create_matching_from_referral(self.sender, nonexistent_referral_id)

    # 매칭이 생성되지 않았는지 확인
    matching_count = Matching.objects.filter(sender=self.sender).count()
    self.assertEqual(matching_count, 0)

  def test_create_matching_with_wrong_user_referral(self):
    """다른 사용자의 추천으로 매칭 생성 시 에러 발생 테스트"""
    # 다른 사용자 생성
    another_user = User.objects.create_user(
      username="another_user",
      email="another@test.com",
      ticket_amount=200,
    )
    Profile.objects.create(user=another_user, gender=Gender.MALE)

    # sender가 아닌 another_user의 추천으로 매칭 생성 시도
    with self.assertRaises(ReferralNotFoundError):
      MatchingCreationService.create_matching_from_referral(another_user, self.referral.id)

  def test_create_duplicate_matching_fails(self):
    """중복 매칭 생성 시 에러 발생 테스트"""
    # 첫 번째 매칭 생성
    MatchingCreationService.create_matching_from_referral(self.sender, self.referral.id)

    # 같은 추천으로 다시 매칭 생성 시도
    with self.assertRaises(ValidationError) as context:
      MatchingCreationService.create_matching_from_referral(self.sender, self.referral.id)

    self.assertIn("이미 해당 사용자에게 호감을 보낸 적이 있습니다", str(context.exception))

  def test_transaction_rollback_on_ticket_deduction_failure(self):
    """티켓 차감 실패 시 트랜잭션 롤백 테스트"""
    # 티켓을 부족하게 설정
    self.sender.ticket_amount = self.ticket_cost - 1
    self.sender.save()

    initial_matching_count = Matching.objects.count()

    # 매칭 생성 시도 (티켓 부족으로 실패)
    try:
      MatchingCreationService.create_matching_from_referral(self.sender, self.referral.id)
    except ValueError:
      pass

    # 매칭이 생성되지 않았는지 확인 (트랜잭션 롤백)
    final_matching_count = Matching.objects.count()
    self.assertEqual(initial_matching_count, final_matching_count)

    # 티켓 로그도 생성되지 않았는지 확인
    ticket_logs = TicketLog.objects.filter(user=self.sender)
    self.assertEqual(ticket_logs.count(), 0)

  def test_check_ticket_availability_sufficient(self):
    """티켓 보유량 확인 - 충분한 경우"""
    self.sender.ticket_amount = self.ticket_cost + 10
    self.sender.save()

    result = MatchingCreationService.check_ticket_availability(self.sender)
    self.assertTrue(result)

  def test_check_ticket_availability_insufficient(self):
    """티켓 보유량 확인 - 부족한 경우"""
    self.sender.ticket_amount = self.ticket_cost - 1
    self.sender.save()

    result = MatchingCreationService.check_ticket_availability(self.sender)
    self.assertFalse(result)

  def test_check_ticket_availability_exact(self):
    """티켓 보유량 확인 - 정확히 필요한 만큼인 경우"""
    self.sender.ticket_amount = self.ticket_cost
    self.sender.save()

    result = MatchingCreationService.check_ticket_availability(self.sender)
    self.assertTrue(result)

  def test_check_ticket_availability_with_custom_amount(self):
    """커스텀 티켓 수량으로 보유량 확인"""
    custom_amount = 75
    self.sender.ticket_amount = 60
    self.sender.save()

    result = MatchingCreationService.check_ticket_availability(self.sender, ticket_amount=custom_amount)
    self.assertFalse(result)

    self.sender.ticket_amount = 80
    self.sender.save()

    result = MatchingCreationService.check_ticket_availability(self.sender, ticket_amount=custom_amount)
    self.assertTrue(result)

  def test_get_required_ticket_amount(self):
    """필요한 티켓 수량 반환 테스트"""
    required_amount = MatchingCreationService.get_required_ticket_amount()
    self.assertEqual(required_amount, self.ticket_cost)

  def test_matching_sent_at_timestamp(self):
    """매칭 생성 시 sent_at 타임스탬프가 설정되는지 테스트"""
    before_creation = timezone.now()

    matching = MatchingCreationService.create_matching_from_referral(self.sender, self.referral.id)

    after_creation = timezone.now()

    # sent_at이 적절한 시간대에 설정되었는지 확인
    self.assertIsNotNone(matching.sent_at)
    self.assertGreaterEqual(matching.sent_at, before_creation)
    self.assertLessEqual(matching.sent_at, after_creation)

  def test_ticket_log_description(self):
    """티켓 사용 로그에 적절한 설명이 포함되는지 테스트"""
    matching = MatchingCreationService.create_matching_from_referral(self.sender, self.referral.id)

    # 로그 확인
    ticket_log = TicketLog.objects.filter(
      user=self.sender,
      category=TicketLogCategory.USE,
      matching=matching,
    ).first()

    # 설명에 수신자 정보가 포함되어 있는지 확인
    self.assertIsNotNone(ticket_log.description)
    self.assertIn(self.receiver.username, ticket_log.description)
    self.assertIn("매칭 생성", ticket_log.description)

  def test_no_ticket_manipulation_vulnerability(self):
    """티켓 수량 조작의 위험이 없는지 테스트"""
    initial_ticket_amount = self.sender.ticket_amount

    # 매칭 생성
    matching = MatchingCreationService.create_matching_from_referral(self.sender, self.referral.id)

    # 데이터베이스에서 직접 조회하여 확인
    sender_from_db = User.objects.get(pk=self.sender.pk)

    # 정확히 ticket_cost만큼만 차감되었는지 확인
    self.assertEqual(
      sender_from_db.ticket_amount,
      initial_ticket_amount - self.ticket_cost,
    )
    self.assertEqual(sender_from_db.used_ticket_amount, self.ticket_cost)

    # 로그와 실제 티켓 수량이 일치하는지 확인
    ticket_log = TicketLog.objects.filter(
      user=self.sender,
      category=TicketLogCategory.USE,
      matching=matching,
    ).first()

    self.assertEqual(ticket_log.amount, self.ticket_cost)

    # 티켓 총량이 보존되는지 확인
    total = sender_from_db.ticket_amount + sender_from_db.used_ticket_amount
    self.assertEqual(total, initial_ticket_amount)

  def test_create_multiple_matchings_to_different_users(self):
    """여러 다른 사용자에게 매칭 생성이 가능한지 테스트"""
    # 다른 수신자 생성
    another_receiver = User.objects.create_user(
      username="another_receiver",
      email="another_receiver@test.com",
      ticket_amount=100,
    )
    Profile.objects.create(user=another_receiver, gender=Gender.FEMALE)

    # 다른 추천 생성
    another_referral = Referral.objects.create(
      user=self.sender,
      referral_user=another_receiver,
      referred_at=timezone.now(),
      referred_algorithm="TestAlgorithm",
    )

    initial_ticket_amount = self.sender.ticket_amount

    # 첫 번째 매칭 생성
    matching1 = MatchingCreationService.create_matching_from_referral(self.sender, self.referral.id)

    # 두 번째 매칭 생성
    matching2 = MatchingCreationService.create_matching_from_referral(self.sender, another_referral.id)

    # 두 매칭 모두 생성되었는지 확인
    self.assertIsNotNone(matching1)
    self.assertIsNotNone(matching2)
    self.assertNotEqual(matching1.id, matching2.id)

    # 티켓이 두 번 차감되었는지 확인
    self.sender.refresh_from_db()
    self.assertEqual(
      self.sender.ticket_amount,
      initial_ticket_amount - (self.ticket_cost * 2),
    )

  def test_matching_initial_state(self):
    """생성된 매칭의 초기 상태가 올바른지 테스트"""
    matching = MatchingCreationService.create_matching_from_referral(self.sender, self.referral.id)

    # 초기 상태 확인
    self.assertIsNone(matching.received_at)
    self.assertIsNone(matching.rejected_at)
    self.assertIsNone(matching.expired_at)
    self.assertIsNotNone(matching.sent_at)
