from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from api.v1.matchmakings.exceptions import MatchingValidationError
from api.v1.matchmakings.services import MatchingActionService
from matchmakings.models import Matching
from profiles.models import Gender, Profile

User = get_user_model()


class MatchingActionServiceTest(TestCase):
  """MatchingActionService 테스트"""

  def setUp(self):
    """테스트 데이터 설정"""
    # 사용자 생성
    self.sender = User.objects.create_user(
        username="sender",
        email="sender@test.com",
        ticket_amount=100,
    )
    self.receiver = User.objects.create_user(
        username="receiver",
        email="receiver@test.com",
        ticket_amount=50,
    )

    # 프로필 생성
    Profile.objects.create(user=self.sender, gender=Gender.MALE)
    Profile.objects.create(user=self.receiver, gender=Gender.FEMALE)

    # 매칭 생성
    self.matching = Matching.objects.create(
        sender=self.sender,
        receiver=self.receiver,
        ticket_amount=10,
        sent_at=timezone.now(),
    )

  def test_accept_matching_success(self):
    """매칭 승인이 정상적으로 처리되는지 테스트"""
    # 승인 처리
    result = MatchingActionService.process_matching_action(self.matching, "accept")

    # 결과 확인
    self.assertIsNotNone(result.received_at)
    self.assertIsNone(result.rejected_at)

    # DB에서 다시 조회하여 확인
    self.matching.refresh_from_db()
    self.assertIsNotNone(self.matching.received_at)
    self.assertIsNone(self.matching.rejected_at)

  def test_reject_matching_success(self):
    """매칭 거부가 정상적으로 처리되는지 테스트"""
    # 거부 처리
    result = MatchingActionService.process_matching_action(self.matching, "reject")

    # 결과 확인
    self.assertIsNone(result.received_at)
    self.assertIsNotNone(result.rejected_at)

    # DB에서 다시 조회하여 확인
    self.matching.refresh_from_db()
    self.assertIsNone(self.matching.received_at)
    self.assertIsNotNone(self.matching.rejected_at)

  def test_invalid_action_raises_error(self):
    """잘못된 액션이 입력되면 에러가 발생하는지 테스트"""
    with self.assertRaises(MatchingValidationError) as context:
      MatchingActionService.process_matching_action(self.matching, "invalid_action")

    self.assertIn("Invalid action", str(context.exception))

  def test_cannot_process_already_accepted_matching(self):
    """이미 승인된 매칭은 다시 처리할 수 없는지 테스트"""
    # 먼저 승인
    MatchingActionService.process_matching_action(self.matching, "accept")

    # 다시 처리 시도
    with self.assertRaises(MatchingValidationError) as context:
      MatchingActionService.process_matching_action(self.matching, "reject")

    self.assertIn("Matching already processed", str(context.exception))

  def test_cannot_process_already_rejected_matching(self):
    """이미 거부된 매칭은 다시 처리할 수 없는지 테스트"""
    # 먼저 거부
    MatchingActionService.process_matching_action(self.matching, "reject")

    # 다시 처리 시도
    with self.assertRaises(MatchingValidationError) as context:
      MatchingActionService.process_matching_action(self.matching, "accept")

    self.assertIn("Matching already processed", str(context.exception))

  def test_accept_sets_received_at_timestamp(self):
    """승인 시 received_at 타임스탬프가 설정되는지 테스트"""
    before_accept = timezone.now()

    # 승인 처리
    MatchingActionService.process_matching_action(self.matching, "accept")

    after_accept = timezone.now()

    # received_at이 적절한 시간대에 설정되었는지 확인
    self.matching.refresh_from_db()
    self.assertIsNotNone(self.matching.received_at)
    self.assertGreaterEqual(self.matching.received_at, before_accept)
    self.assertLessEqual(self.matching.received_at, after_accept)

  def test_reject_sets_rejected_at_timestamp(self):
    """거부 시 rejected_at 타임스탬프가 설정되는지 테스트"""
    before_reject = timezone.now()

    # 거부 처리
    MatchingActionService.process_matching_action(self.matching, "reject")

    after_reject = timezone.now()

    # rejected_at이 적절한 시간대에 설정되었는지 확인
    self.matching.refresh_from_db()
    self.assertIsNotNone(self.matching.rejected_at)
    self.assertGreaterEqual(self.matching.rejected_at, before_reject)
    self.assertLessEqual(self.matching.rejected_at, after_reject)

  def test_accept_clears_rejected_at(self):
    """승인 시 rejected_at이 None으로 설정되는지 테스트"""
    # 승인 처리
    result = MatchingActionService.process_matching_action(self.matching, "accept")

    # rejected_at이 None인지 확인
    self.assertIsNone(result.rejected_at)
    self.matching.refresh_from_db()
    self.assertIsNone(self.matching.rejected_at)

  def test_reject_clears_received_at(self):
    """거부 시 received_at이 None으로 설정되는지 테스트"""
    # 거부 처리
    result = MatchingActionService.process_matching_action(self.matching, "reject")

    # received_at이 None인지 확인
    self.assertIsNone(result.received_at)
    self.matching.refresh_from_db()
    self.assertIsNone(self.matching.received_at)

  def test_transaction_rollback_on_error(self):
    """에러 발생 시 트랜잭션이 롤백되는지 테스트"""
    # 초기 상태 저장
    initial_received_at = self.matching.received_at
    initial_rejected_at = self.matching.rejected_at

    # 잘못된 액션으로 에러 발생
    try:
      MatchingActionService.process_matching_action(self.matching, "invalid")
    except MatchingValidationError:
      pass

    # DB에서 다시 조회
    self.matching.refresh_from_db()

    # 상태가 변경되지 않았는지 확인
    self.assertEqual(self.matching.received_at, initial_received_at)
    self.assertEqual(self.matching.rejected_at, initial_rejected_at)

  def test_process_multiple_matchings_independently(self):
    """여러 매칭이 독립적으로 처리되는지 테스트"""
    # 다른 매칭 생성
    another_receiver = User.objects.create_user(
        username="another_receiver",
        email="another_receiver@test.com",
        ticket_amount=50,
    )
    Profile.objects.create(user=another_receiver, gender=Gender.FEMALE)

    another_matching = Matching.objects.create(
        sender=self.sender,
        receiver=another_receiver,
        ticket_amount=10,
        sent_at=timezone.now(),
    )

    # 첫 번째 매칭은 승인, 두 번째는 거부
    MatchingActionService.process_matching_action(self.matching, "accept")
    MatchingActionService.process_matching_action(another_matching, "reject")

    # 각각 올바르게 처리되었는지 확인
    self.matching.refresh_from_db()
    another_matching.refresh_from_db()

    self.assertIsNotNone(self.matching.received_at)
    self.assertIsNone(self.matching.rejected_at)

    self.assertIsNone(another_matching.received_at)
    self.assertIsNotNone(another_matching.rejected_at)

  def test_action_is_case_sensitive(self):
    """액션이 대소문자를 구분하는지 테스트"""
    # 대문자로 시도
    with self.assertRaises(MatchingValidationError):
      MatchingActionService.process_matching_action(self.matching, "ACCEPT")

    # 혼합 케이스로 시도
    with self.assertRaises(MatchingValidationError):
      MatchingActionService.process_matching_action(self.matching, "Accept")

    # 올바른 케이스로 시도
    result = MatchingActionService.process_matching_action(self.matching, "accept")
    self.assertIsNotNone(result.received_at)

  def test_matching_remains_unchanged_after_error(self):
    """에러 발생 후 매칭 상태가 변경되지 않는지 테스트"""
    # 초기 상태 확인
    self.assertIsNone(self.matching.received_at)
    self.assertIsNone(self.matching.rejected_at)

    # 잘못된 액션으로 에러 발생
    with self.assertRaises(MatchingValidationError):
      MatchingActionService.process_matching_action(self.matching, "wrong_action")

    # 상태가 그대로인지 확인
    self.matching.refresh_from_db()
    self.assertIsNone(self.matching.received_at)
    self.assertIsNone(self.matching.rejected_at)
    self.assertIsNone(self.matching.expired_at)

  def test_returns_updated_matching_object(self):
    """처리 후 업데이트된 매칭 객체를 반환하는지 테스트"""
    result = MatchingActionService.process_matching_action(self.matching, "accept")

    # 반환된 객체가 Matching 인스턴스인지 확인
    self.assertIsInstance(result, Matching)

    # 반환된 객체가 업데이트된 상태를 포함하는지 확인
    self.assertIsNotNone(result.received_at)
    self.assertEqual(result.id, self.matching.id)
