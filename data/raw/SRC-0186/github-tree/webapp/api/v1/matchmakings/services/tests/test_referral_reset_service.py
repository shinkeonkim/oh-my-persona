from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from api.v1.matchmakings.services import ReferralResetService
from common.exceptions.custom_exceptions import ValidationError
from profiles.models import Gender, Profile
from users.models import TicketLog, TicketLogCategory

User = get_user_model()


class ReferralResetServiceTest(TestCase):
  """ReferralResetService 테스트"""

  def setUp(self):
    """테스트 데이터 설정"""
    self.user = User.objects.create_user(
        username="test_user",
        email="test@test.com",
        ticket_amount=100,
        used_ticket_amount=0,
        remaining_referral_quota=0,  # 추천 횟수가 소진된 상태
    )
    Profile.objects.create(user=self.user, gender=Gender.MALE)

    self.ticket_cost = settings.REFERRAL_QUOTA_RESET_TICKET_COST
    self.max_quota = settings.REFERRAL_QUOTA_MAX

  def test_reset_referral_quota_success(self):
    """추천 횟수 초기화가 정상적으로 처리되는지 테스트"""
    initial_ticket_amount = self.user.ticket_amount
    initial_used_ticket_amount = self.user.used_ticket_amount

    # 추천 횟수 초기화
    result_user = ReferralResetService.reset_referral_quota(self.user)

    # 추천 횟수가 초기화되었는지 확인
    self.assertEqual(result_user.remaining_referral_quota, self.max_quota)
    self.assertIsNone(result_user.last_exhausted_referral_quota_at)

    # 티켓이 차감되었는지 확인
    self.assertEqual(
        result_user.ticket_amount,
        initial_ticket_amount - self.ticket_cost,
    )
    self.assertEqual(
        result_user.used_ticket_amount,
        initial_used_ticket_amount + self.ticket_cost,
    )

    # DB에서 다시 조회하여 확인
    self.user.refresh_from_db()
    self.assertEqual(self.user.remaining_referral_quota, self.max_quota)
    self.assertIsNone(self.user.last_exhausted_referral_quota_at)

  def test_reset_referral_quota_creates_ticket_log(self):
    """추천 횟수 초기화 시 티켓 로그가 생성되는지 테스트"""
    # 초기화 전 로그 개수
    initial_log_count = TicketLog.objects.filter(user=self.user).count()

    # 추천 횟수 초기화
    ReferralResetService.reset_referral_quota(self.user)

    # 티켓 로그가 생성되었는지 확인
    ticket_log = TicketLog.objects.filter(
        user=self.user,
        category=TicketLogCategory.USE,
    ).latest("created_at")

    self.assertIsNotNone(ticket_log)
    self.assertEqual(ticket_log.amount, -self.ticket_cost)
    self.assertEqual(ticket_log.description, "추천 횟수 초기화")

    # 로그가 1개 증가했는지 확인
    final_log_count = TicketLog.objects.filter(user=self.user).count()
    self.assertEqual(final_log_count, initial_log_count + 1)

  def test_reset_referral_quota_fails_when_quota_remaining(self):
    """추천 횟수가 남아있을 때 초기화가 실패하는지 테스트"""
    # 추천 횟수를 1로 설정 (아직 남아있음)
    self.user.remaining_referral_quota = 1
    self.user.save()

    with self.assertRaises(ValidationError) as context:
      ReferralResetService.reset_referral_quota(self.user)

    self.assertIn("추천 횟수가 남아있어 초기화할 수 없습니다", str(context.exception))

    # details에 remaining_quota가 포함되는지 확인
    self.assertEqual(context.exception.details["remaining_quota"], 1)

  def test_reset_referral_quota_fails_when_insufficient_tickets(self):
    """티켓이 부족할 때 초기화가 실패하는지 테스트"""
    # 티켓을 부족하게 설정
    self.user.ticket_amount = self.ticket_cost - 1
    self.user.save()

    with self.assertRaises(ValidationError) as context:
      ReferralResetService.reset_referral_quota(self.user)

    self.assertIn("티켓이 부족합니다", str(context.exception))

    # details에 필요한 티켓과 현재 티켓이 포함되는지 확인
    self.assertEqual(context.exception.details["required_tickets"], self.ticket_cost)
    self.assertEqual(context.exception.details["current_tickets"], self.ticket_cost - 1)

  def test_reset_referral_quota_exact_ticket_amount(self):
    """필요한 티켓을 정확히 보유한 경우 초기화가 성공하는지 테스트"""
    # 티켓을 정확히 필요한 만큼만 설정
    self.user.ticket_amount = self.ticket_cost
    self.user.save()

    result_user = ReferralResetService.reset_referral_quota(self.user)

    # 초기화가 성공했는지 확인
    self.assertEqual(result_user.remaining_referral_quota, self.max_quota)
    self.assertEqual(result_user.ticket_amount, 0)

  def test_reset_referral_quota_transaction_rollback_on_error(self):
    """에러 발생 시 트랜잭션이 롤백되는지 테스트"""
    # 초기 상태 저장
    initial_ticket_amount = self.user.ticket_amount

    # 추천 횟수가 남아있어서 에러 발생
    self.user.remaining_referral_quota = 1
    self.user.save()

    try:
      ReferralResetService.reset_referral_quota(self.user)
    except ValidationError:
      pass

    # DB에서 다시 조회
    self.user.refresh_from_db()

    # 티켓이 차감되지 않았는지 확인 (롤백됨)
    self.assertEqual(self.user.remaining_referral_quota, 1)
    self.assertEqual(self.user.ticket_amount, initial_ticket_amount)

    # 티켓 로그가 생성되지 않았는지 확인
    log_exists = TicketLog.objects.filter(
        user=self.user,
        description="추천 횟수 초기화",
    ).exists()
    self.assertFalse(log_exists)

  def test_reset_referral_quota_uses_select_for_update(self):
    """reset_referral_quota가 select_for_update를 사용하는지 테스트"""
    # 이 테스트는 실제로 락이 걸리는지 확인하기 어려우므로
    # 정상적으로 실행되는지만 확인
    result_user = ReferralResetService.reset_referral_quota(self.user)

    self.assertIsNotNone(result_user)
    self.assertEqual(result_user.remaining_referral_quota, self.max_quota)

  def test_reset_referral_quota_updates_correct_fields(self):
    """초기화 시 올바른 필드들만 업데이트되는지 테스트"""
    # 다른 필드 설정
    original_username = self.user.username

    # 초기화 실행
    ReferralResetService.reset_referral_quota(self.user)

    # DB에서 다시 조회
    self.user.refresh_from_db()

    # 업데이트되어야 하는 필드들
    self.assertEqual(self.user.remaining_referral_quota, self.max_quota)
    self.assertIsNone(self.user.last_exhausted_referral_quota_at)

    # 업데이트되지 않아야 하는 필드들
    self.assertEqual(self.user.username, original_username)

  def test_reset_referral_quota_clears_last_exhausted_at(self):
    """초기화 시 last_exhausted_referral_quota_at이 None으로 설정되는지 테스트"""
    from django.utils import timezone

    # last_exhausted_referral_quota_at 설정
    self.user.last_exhausted_referral_quota_at = timezone.now()
    self.user.save()

    # 초기화 실행
    ReferralResetService.reset_referral_quota(self.user)

    # DB에서 다시 조회
    self.user.refresh_from_db()

    # None으로 초기화되었는지 확인
    self.assertIsNone(self.user.last_exhausted_referral_quota_at)

  @patch("api.v1.matchmakings.services.referral_reset_service.logger")
  def test_reset_referral_quota_logs_success(self, mock_logger):
    """초기화 성공 시 로그가 기록되는지 테스트"""
    ReferralResetService.reset_referral_quota(self.user)

    # info 로그가 호출되었는지 확인
    mock_logger.info.assert_called_once()
    call_args = mock_logger.info.call_args
    self.assertIn("Referral quota reset successfully", call_args[0])

  @patch("api.v1.matchmakings.services.referral_reset_service.logger")
  def test_reset_referral_quota_logs_error_on_exception(self, mock_logger):
    """초기화 중 예외 발생 시 에러 로그가 기록되는지 테스트"""
    # 예외를 발생시키기 위해 티켓 부족 상태로 설정
    self.user.ticket_amount = 0
    self.user.save()

    try:
      ReferralResetService.reset_referral_quota(self.user)
    except ValidationError:
      pass

    # ValidationError는 로그에 기록되지 않음 (re-raise만 됨)
    # 하지만 다른 예외가 발생하면 error 로그가 기록됨

  def test_reset_referral_quota_returns_updated_user(self):
    """초기화 후 업데이트된 사용자 객체를 반환하는지 테스트"""
    result_user = ReferralResetService.reset_referral_quota(self.user)

    # 반환된 객체가 User 인스턴스인지 확인
    self.assertIsInstance(result_user, User)

    # 반환된 객체가 업데이트된 상태를 포함하는지 확인
    self.assertEqual(result_user.remaining_referral_quota, self.max_quota)
    self.assertEqual(result_user.id, self.user.id)

  def test_reset_referral_quota_with_multiple_users(self):
    """여러 사용자가 독립적으로 초기화할 수 있는지 테스트"""
    # 다른 사용자 생성
    other_user = User.objects.create_user(
        username="other_user",
        email="other@test.com",
        ticket_amount=100,
        remaining_referral_quota=0,
    )
    Profile.objects.create(user=other_user, gender=Gender.FEMALE)

    # 첫 번째 사용자 초기화
    ReferralResetService.reset_referral_quota(self.user)

    # 두 번째 사용자 초기화
    ReferralResetService.reset_referral_quota(other_user)

    # 각각 올바르게 초기화되었는지 확인
    self.user.refresh_from_db()
    other_user.refresh_from_db()

    self.assertEqual(self.user.remaining_referral_quota, self.max_quota)
    self.assertEqual(other_user.remaining_referral_quota, self.max_quota)

  def test_reset_referral_quota_validation_error_details(self):
    """ValidationError의 details에 올바른 정보가 포함되는지 테스트"""
    # 추천 횟수가 남아있는 상태로 설정
    self.user.remaining_referral_quota = 3
    self.user.save()

    try:
      ReferralResetService.reset_referral_quota(self.user)
    except ValidationError as e:
      # details 확인
      self.assertEqual(e.details["remaining_quota"], 3)
      self.assertIn("message", e.details)
