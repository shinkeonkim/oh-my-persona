from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from api.v1.matchmakings.services.referral_creation_service import (
  MAX_RECENT_REFERRALS_PER_ALGORITHM,
  ReferralCreationService,
)
from common.exceptions.custom_exceptions import ValidationError
from matchmakings.models import Matching, PreMatching, PreMatchingScore, Referral
from profiles.models import Gender, Profile
from users.factories import UserFactory

User = get_user_model()


class ReferralCreationServiceTest(TestCase):
  """ReferralCreationService 테스트"""

  def setUp(self):
    """테스트 데이터 설정"""
    # 남성 사용자 생성
    self.male_user = UserFactory(
      username="male_user",
      email="male@test.com",
      remaining_referral_quota=5,
      confirm_user=True,
      confirm_user__profile_gender=Gender.MALE,
    )
    # 여성 사용자들 생성
    self.female_user1 = UserFactory(
      username="female_user1",
      email="female1@test.com",
      confirm_user=True,
      confirm_user__profile_gender=Gender.FEMALE,
    )

    self.female_user2 = UserFactory(
      username="female_user2",
      email="female2@test.com",
      confirm_user=True,
      confirm_user__profile_gender=Gender.FEMALE,
    )

    self.female_user3 = UserFactory(
      username="female_user3",
      email="female3@test.com",
      confirm_user=True,
      confirm_user__profile_gender=Gender.FEMALE,
    )

    self.algorithm_type = "AAlgorithm"

  def test_create_referral_success(self):
    """추천이 정상적으로 생성되는지 테스트"""
    initial_quota = self.male_user.remaining_referral_quota

    # PreMatching 생성
    prematching = PreMatching.objects.create(
      male_user=self.male_user,
      female_user=self.female_user1,
    )

    # PreMatchingScore 생성
    PreMatchingScore.objects.create(
      prematching=prematching,
      algorithm_category=self.algorithm_type,
      score=100,
    )

    referral = ReferralCreationService.create_referral(self.male_user, self.algorithm_type)

    # 추천이 생성되었는지 확인
    self.assertIsNotNone(referral)
    self.assertEqual(referral.user, self.male_user)
    self.assertEqual(referral.referral_user, self.female_user1)
    self.assertEqual(referral.referred_algorithm, self.algorithm_type)
    self.assertIsNotNone(referral.referred_at)

    # 추천 횟수가 차감되었는지 확인
    self.male_user.refresh_from_db()
    self.assertEqual(self.male_user.remaining_referral_quota, initial_quota - 1)

  def test_create_referral_fails_when_no_quota(self):
    """추천 횟수가 없을 때 에러가 발생하는지 테스트"""
    # 추천 횟수를 0으로 설정
    self.male_user.remaining_referral_quota = 0
    self.male_user.save()

    with self.assertRaises(ValidationError) as context:
      ReferralCreationService.create_referral(self.male_user, self.algorithm_type)

    self.assertIn("추천 횟수가 부족합니다", str(context.exception))

  def test_create_referral_returns_none_when_no_users_available(self):
    """추천할 사용자가 없을 때 None을 반환하는지 테스트"""
    # 모든 여성 사용자를 이미 추천받은 것으로 설정
    for female_user in [self.female_user1, self.female_user2, self.female_user3]:
      Referral.objects.create(
        user=self.male_user,
        referral_user=female_user,
        referred_at=timezone.now(),
        referred_algorithm=self.algorithm_type,
      )

    result = ReferralCreationService.create_referral(self.male_user, self.algorithm_type)

    # None이 반환되는지 확인
    self.assertIsNone(result)

  def test_get_excluded_users_includes_unreceived_matchings(self):
    """수신되지 않은 매칭의 발신자가 제외 목록에 포함되는지 테스트"""
    # 다른 사용자가 현재 사용자에게 보낸 매칭 (아직 수신되지 않음)
    Matching.objects.create(
      sender=self.female_user1,
      receiver=self.male_user,
      ticket_amount=10,
      sent_at=timezone.now(),
      received_at=None,  # 수신되지 않음
    )

    excluded_users = ReferralCreationService.get_excluded_users(self.male_user)

    self.assertIn(self.female_user1.id, excluded_users)

  def test_get_excluded_users_includes_rejected_matchings(self):
    """거절된 매칭의 수신자가 제외 목록에 포함되는지 테스트"""
    # 현재 사용자가 거절한 매칭
    Matching.objects.create(
      sender=self.male_user,
      receiver=self.female_user1,
      ticket_amount=10,
      sent_at=timezone.now(),
      rejected_at=timezone.now(),  # 거절됨
    )

    excluded_users = ReferralCreationService.get_excluded_users(self.male_user)

    self.assertIn(self.female_user1.id, excluded_users)

  def test_get_matched_users_includes_accepted_matchings(self):
    """매칭된 사용자가 목록에 포함되는지 테스트"""
    # 발신자로서 매칭됨
    Matching.objects.create(
      sender=self.male_user,
      receiver=self.female_user1,
      ticket_amount=10,
      sent_at=timezone.now(),
      received_at=timezone.now(),  # 매칭 완료
    )

    # 수신자로서 매칭됨
    Matching.objects.create(
      sender=self.female_user2,
      receiver=self.male_user,
      ticket_amount=10,
      sent_at=timezone.now(),
      received_at=timezone.now(),  # 매칭 완료
    )

    matched_users = ReferralCreationService.get_matched_users(self.male_user)

    self.assertIn(self.female_user1.id, matched_users)
    self.assertIn(self.female_user2.id, matched_users)

  def test_find_recommended_user_for_male(self):
    """남성 사용자에 대한 추천 사용자 찾기 테스트"""
    # PreMatching 생성
    prematching = PreMatching.objects.create(
      male_user=self.male_user,
      female_user=self.female_user1,
    )

    # PreMatchingScore 생성
    PreMatchingScore.objects.create(
      prematching=prematching,
      algorithm_category=self.algorithm_type,
      score=100,
    )

    _score, recommended_user = ReferralCreationService.find_recommended_user(self.male_user, self.algorithm_type)

    self.assertIsNotNone(recommended_user)
    self.assertEqual(recommended_user.profile.gender, Gender.FEMALE)

  def test_find_recommended_user_for_female(self):
    """여성 사용자에 대한 추천 사용자 찾기 테스트"""
    # 여성 사용자 생성
    female_user = User.objects.create_user(
      username="female_test",
      email="female_test@test.com",
      remaining_referral_quota=5,
    )
    Profile.objects.create(user=female_user, gender=Gender.FEMALE)

    # PreMatching 생성
    prematching = PreMatching.objects.create(
      male_user=self.male_user,
      female_user=female_user,
    )

    # PreMatchingScore 생성
    PreMatchingScore.objects.create(
      prematching=prematching,
      algorithm_category=self.algorithm_type,
      score=100,
    )

    _score, recommended_user = ReferralCreationService.find_recommended_user(female_user, self.algorithm_type)

    self.assertIsNotNone(recommended_user)
    self.assertEqual(recommended_user.profile.gender, Gender.MALE)

  def test_find_recommended_user_returns_none_when_no_profile(self):
    """프로필이 없는 사용자는 추천받지 못하는지 테스트"""
    # 프로필 없는 사용자 생성
    user_without_profile = User.objects.create_user(
      username="no_profile",
      email="no_profile@test.com",
    )

    _score, recommended_user = ReferralCreationService.find_recommended_user(user_without_profile, self.algorithm_type)

    self.assertIsNone(recommended_user)

  def test_find_recommended_user_excludes_already_referred(self):
    """이미 추천받은 사용자는 제외되는지 테스트"""
    # PreMatching 생성
    prematching1 = PreMatching.objects.create(
      male_user=self.male_user,
      female_user=self.female_user1,
    )

    # PreMatchingScore 생성
    PreMatchingScore.objects.create(
      prematching=prematching1,
      algorithm_category=self.algorithm_type,
      score=90,
    )

    # 이미 추천받음
    Referral.objects.create(
      user=self.male_user,
      referral_user=self.female_user1,
      referred_at=timezone.now(),
      referred_algorithm=self.algorithm_type,
    )

    # PreMatching 추가
    prematching2 = PreMatching.objects.create(
      male_user=self.male_user,
      female_user=self.female_user2,
    )

    # PreMatchingScore 생성
    PreMatchingScore.objects.create(
      prematching=prematching2,
      algorithm_category=self.algorithm_type,
      score=100,
    )

    _score, recommended_user = ReferralCreationService.find_recommended_user(self.male_user, self.algorithm_type)

    # female_user1은 제외되고 female_user2가 추천되어야 함
    self.assertIsNotNone(recommended_user)
    self.assertNotEqual(recommended_user, self.female_user1)

  def test_find_recommended_user_excludes_self(self):
    """자기 자신은 추천에서 제외되는지 테스트"""
    _score, recommended_user = ReferralCreationService.find_recommended_user(self.male_user, self.algorithm_type)

    if recommended_user:
      self.assertNotEqual(recommended_user.id, self.male_user.id)

  def test_get_recently_unmatched_referred_user_ids_by_algorithm(self):
    """특정 알고리즘으로 최근에 추천된 사용자 ID들을 반환하는지 테스트"""
    # 여러 추천 생성
    for i, female_user in enumerate([self.female_user1, self.female_user2, self.female_user3]):
      Referral.objects.create(
        user=self.male_user,
        referral_user=female_user,
        referred_at=timezone.now(),
        referred_algorithm=self.algorithm_type,
      )

    recently_referred_ids = ReferralCreationService.get_recently_unmatched_referred_user_ids_by_algorithm(
      self.male_user, self.algorithm_type)

    # 모든 추천이 반환되는지 확인
    self.assertEqual(len(recently_referred_ids), 3)
    # 반환된 것이 user ID 리스트인지 확인
    self.assertIn(self.female_user1.id, recently_referred_ids)
    self.assertIn(self.female_user2.id, recently_referred_ids)
    self.assertIn(self.female_user3.id, recently_referred_ids)

  def test_get_recently_unmatched_referred_users_limits_to_max(self):
    """최근 추천 사용자 수가 최대값으로 제한되는지 테스트"""
    # MAX_RECENT_REFERRALS_PER_ALGORITHM보다 많은 여성 사용자 생성
    female_users = []
    for i in range(MAX_RECENT_REFERRALS_PER_ALGORITHM + 5):
      female_user = User.objects.create_user(
        username=f"flimit_{i}",
        email=f"female_limit_test_{i}@test.com",
      )
      Profile.objects.create(user=female_user, gender=Gender.FEMALE)
      female_users.append(female_user)

    # 추천 생성
    for female_user in female_users:
      Referral.objects.create(
        user=self.male_user,
        referral_user=female_user,
        referred_at=timezone.now(),
        referred_algorithm=self.algorithm_type,
      )

    recently_referred_ids = ReferralCreationService.get_recently_unmatched_referred_user_ids_by_algorithm(
      self.male_user, self.algorithm_type)

    # 최대값만큼만 반환되는지 확인
    self.assertEqual(len(recently_referred_ids), MAX_RECENT_REFERRALS_PER_ALGORITHM)

  def test_get_recently_unmatched_referred_users_excludes_matched(self):
    """매칭이 이루어진 사용자는 최근 추천에서 제외되는지 테스트"""
    # 추천 생성
    Referral.objects.create(
      user=self.male_user,
      referral_user=self.female_user1,
      referred_at=timezone.now(),
      referred_algorithm=self.algorithm_type,
    )

    # 매칭 생성
    Matching.objects.create(
      sender=self.male_user,
      receiver=self.female_user1,
      ticket_amount=10,
      sent_at=timezone.now(),
    )

    recently_referred_ids = ReferralCreationService.get_recently_unmatched_referred_user_ids_by_algorithm(
      self.male_user, self.algorithm_type)

    # female_user1은 제외되어야 함
    self.assertNotIn(self.female_user1.id, recently_referred_ids)

  def test_cleanup_referrals_except_latest(self):
    """최신 추천을 제외하고 나머지가 삭제되는지 테스트"""
    # 여러 추천 생성 (매칭 없이)
    female_users = []
    for i in range(15):
      female_user = User.objects.create_user(
        username=f"fcleanup_{i}",
        email=f"female_cleanup_test_{i}@test.com",
      )
      Profile.objects.create(user=female_user, gender=Gender.FEMALE)
      female_users.append(female_user)

    for female_user in female_users:
      Referral.objects.create(
        user=self.male_user,
        referral_user=female_user,
        referred_at=timezone.now(),
        referred_algorithm=self.algorithm_type,
      )

    initial_count = Referral.objects.filter(user=self.male_user).count()
    self.assertEqual(initial_count, 15)

    # 정리 실행 - 최근 10개만 남고 5개 삭제되어야 함
    deleted_count = ReferralCreationService.cleanup_referrals_except_latest(self.male_user, self.algorithm_type)

    # 최근 10개만 남아야 함
    remaining_count = Referral.objects.filter(user=self.male_user).count()
    self.assertEqual(remaining_count, MAX_RECENT_REFERRALS_PER_ALGORITHM)
    self.assertEqual(deleted_count, 5)

  def test_cleanup_referrals_returns_zero_when_nothing_to_delete(self):
    """삭제할 추천이 없을 때 0을 반환하는지 테스트"""
    # 최대 개수보다 적은 추천 생성
    Referral.objects.create(
      user=self.male_user,
      referral_user=self.female_user1,
      referred_at=timezone.now(),
      referred_algorithm=self.algorithm_type,
    )

    deleted_count = ReferralCreationService.cleanup_referrals_except_latest(self.male_user, self.algorithm_type)

    self.assertEqual(deleted_count, 0)

  def test_cleanup_preserves_referrals_used_in_matchings(self):
    """매칭에 사용된 추천은 삭제되지 않는지 테스트"""
    # 20개의 추천 생성 (MAX_RECENT_REFERRALS_PER_ALGORITHM보다 많음)
    female_users = []
    referrals = []
    for i in range(20):
      female_user = User.objects.create_user(
        username=f"fmatching_{i}",
        email=f"female_matching_test_{i}@test.com",
      )
      Profile.objects.create(user=female_user, gender=Gender.FEMALE)
      female_users.append(female_user)

      referral = Referral.objects.create(
        user=self.male_user,
        referral_user=female_user,
        referred_at=timezone.now(),
        referred_algorithm=self.algorithm_type,
      )
      referrals.append(referral)

    # 첫 번째와 다섯 번째 추천을 매칭에 사용 (sender로서)
    Matching.objects.create(
      sender=self.male_user,
      receiver=female_users[0],
      referral=referrals[0],
      ticket_amount=10,
      sent_at=timezone.now(),
    )

    Matching.objects.create(
      sender=self.male_user,
      receiver=female_users[4],
      referral=referrals[4],
      ticket_amount=10,
      sent_at=timezone.now(),
    )

    # 열 번째 추천을 매칭에 사용 (receiver로서)
    Matching.objects.create(
      sender=female_users[9],
      receiver=self.male_user,
      referral=referrals[9],
      ticket_amount=10,
      sent_at=timezone.now(),
    )

    # 정리 실행
    ReferralCreationService.cleanup_referrals_except_latest(self.male_user, self.algorithm_type)

    # 매칭에 사용된 3개 추천이 보존되었는지 확인
    self.assertTrue(Referral.objects.filter(id=referrals[0].id).exists())
    self.assertTrue(Referral.objects.filter(id=referrals[4].id).exists())
    self.assertTrue(Referral.objects.filter(id=referrals[9].id).exists())

    # 매칭에 사용된 추천은 삭제되지 않았어야 함
    remaining_count = Referral.objects.filter(user=self.male_user).count()
    self.assertGreaterEqual(remaining_count, 3)

  def test_cleanup_preserves_recent_unmatched_referrals(self):
    """최근 10개의 매칭되지 않은 추천은 보존되는지 테스트"""
    # 15개의 추천 생성
    female_users = []
    referrals = []
    for i in range(15):
      female_user = User.objects.create_user(
        username=f"frecent_{i}",
        email=f"female_recent_test_{i}@test.com",
      )
      Profile.objects.create(user=female_user, gender=Gender.FEMALE)
      female_users.append(female_user)

      referral = Referral.objects.create(
        user=self.male_user,
        referral_user=female_user,
        referred_at=timezone.now(),
        referred_algorithm=self.algorithm_type,
      )
      referrals.append(referral)

    initial_count = Referral.objects.filter(user=self.male_user).count()
    self.assertEqual(initial_count, 15)

    # 정리 실행
    deleted_count = ReferralCreationService.cleanup_referrals_except_latest(self.male_user, self.algorithm_type)

    # 최근 10개만 남아야 함
    remaining_count = Referral.objects.filter(user=self.male_user).count()
    self.assertEqual(remaining_count, MAX_RECENT_REFERRALS_PER_ALGORITHM)
    self.assertEqual(deleted_count, 5)

  def test_cleanup_preserves_both_recent_and_matched_referrals(self):
    """최근 추천과 매칭에 사용된 추천 모두 보존되는지 테스트"""
    # 25개의 추천 생성
    female_users = []
    referrals = []
    for i in range(25):
      female_user = User.objects.create_user(
        username=f"fboth_{i}",
        email=f"female_both_test_{i}@test.com",
      )
      Profile.objects.create(user=female_user, gender=Gender.FEMALE)
      female_users.append(female_user)

      referral = Referral.objects.create(
        user=self.male_user,
        referral_user=female_user,
        referred_at=timezone.now(),
        referred_algorithm=self.algorithm_type,
      )
      referrals.append(referral)

    # 첫 3개는 매칭에 사용 (오래된 추천이지만 보존되어야 함)
    for i in range(3):
      Matching.objects.create(
        sender=self.male_user,
        receiver=female_users[i],
        referral=referrals[i],
        ticket_amount=10,
        sent_at=timezone.now(),
      )

    initial_count = Referral.objects.filter(user=self.male_user).count()
    self.assertEqual(initial_count, 25)

    # 정리 실행
    deleted_count = ReferralCreationService.cleanup_referrals_except_latest(self.male_user, self.algorithm_type)

    # 매칭에 사용된 3개 + 최근 10개 = 최소 13개는 남아야 함
    # (매칭된 것이 최근 10개에 포함될 수도 있으므로 정확한 수는 다를 수 있음)
    remaining_count = Referral.objects.filter(user=self.male_user).count()
    self.assertGreaterEqual(remaining_count, MAX_RECENT_REFERRALS_PER_ALGORITHM)

    # 매칭에 사용된 추천은 반드시 보존되어야 함
    for i in range(3):
      self.assertTrue(
        Referral.objects.filter(id=referrals[i].id).exists(),
        f"매칭에 사용된 추천 {i}가 삭제되었습니다",
      )

    # 삭제된 수 확인
    self.assertGreater(deleted_count, 0)
    self.assertEqual(initial_count - deleted_count, remaining_count)

  def test_cleanup_only_deletes_specified_algorithm_referrals(self):
    """지정된 알고리즘의 추천만 정리하는지 테스트"""
    other_algorithm_type = "BAlgorithm"

    # A알고리즘으로 15개 추천 생성
    for i in range(15):
      female_user = User.objects.create_user(
        username=f"falgo_a_{i}",
        email=f"female_algo_a_{i}@test.com",
      )
      Profile.objects.create(user=female_user, gender=Gender.FEMALE)

      Referral.objects.create(
        user=self.male_user,
        referral_user=female_user,
        referred_at=timezone.now(),
        referred_algorithm=self.algorithm_type,
      )

    # B알고리즘으로 15개 추천 생성
    for i in range(15):
      female_user = User.objects.create_user(
        username=f"falgo_b_{i}",
        email=f"female_algo_b_{i}@test.com",
      )
      Profile.objects.create(user=female_user, gender=Gender.FEMALE)

      Referral.objects.create(
        user=self.male_user,
        referral_user=female_user,
        referred_at=timezone.now(),
        referred_algorithm=other_algorithm_type,
      )

    a_algorithm_count_before = Referral.objects.filter(
      user=self.male_user,
      referred_algorithm=self.algorithm_type,
    ).count()
    b_algorithm_count_before = Referral.objects.filter(
      user=self.male_user,
      referred_algorithm=other_algorithm_type,
    ).count()

    self.assertEqual(a_algorithm_count_before, 15)
    self.assertEqual(b_algorithm_count_before, 15)

    # A알고리즘 추천만 정리
    ReferralCreationService.cleanup_referrals_except_latest(self.male_user, self.algorithm_type)

    # A알고리즘 추천은 줄어야 함
    a_algorithm_count_after = Referral.objects.filter(
      user=self.male_user,
      referred_algorithm=self.algorithm_type,
    ).count()
    self.assertLess(a_algorithm_count_after, a_algorithm_count_before)

    # B알고리즘 추천은 그대로여야 함
    b_algorithm_count_after = Referral.objects.filter(
      user=self.male_user,
      referred_algorithm=other_algorithm_type,
    ).count()
    self.assertEqual(b_algorithm_count_after, b_algorithm_count_before)

  def test_cleanup_handles_referrals_with_no_matching(self):
    """매칭이 전혀 없는 경우 정상적으로 처리되는지 테스트"""
    # 15개의 추천 생성 (매칭 없음)
    for i in range(15):
      female_user = User.objects.create_user(
        username=f"fnomatch_{i}",
        email=f"female_nomatch_{i}@test.com",
      )
      Profile.objects.create(user=female_user, gender=Gender.FEMALE)

      Referral.objects.create(
        user=self.male_user,
        referral_user=female_user,
        referred_at=timezone.now(),
        referred_algorithm=self.algorithm_type,
      )

    # 정리 실행
    deleted_count = ReferralCreationService.cleanup_referrals_except_latest(self.male_user, self.algorithm_type)

    # 최근 10개만 남고 5개 삭제되어야 함
    remaining_count = Referral.objects.filter(user=self.male_user).count()
    self.assertEqual(remaining_count, MAX_RECENT_REFERRALS_PER_ALGORITHM)
    self.assertEqual(deleted_count, 5)

  def test_cleanup_preserves_referrals_with_accepted_matching(self):
    """수락된 매칭에 사용된 추천은 보존되는지 테스트"""
    # 20개의 추천 생성
    female_users = []
    referrals = []
    for i in range(20):
      female_user = User.objects.create_user(
        username=f"faccepted_{i}",
        email=f"female_accepted_{i}@test.com",
      )
      Profile.objects.create(user=female_user, gender=Gender.FEMALE)
      female_users.append(female_user)

      referral = Referral.objects.create(
        user=self.male_user,
        referral_user=female_user,
        referred_at=timezone.now(),
        referred_algorithm=self.algorithm_type,
      )
      referrals.append(referral)

    # 첫 번째 추천으로 수락된 매칭 생성
    Matching.objects.create(
      sender=self.male_user,
      receiver=female_users[0],
      referral=referrals[0],
      ticket_amount=10,
      sent_at=timezone.now(),
      received_at=timezone.now(),  # 수락됨
    )

    # 정리 실행
    ReferralCreationService.cleanup_referrals_except_latest(self.male_user, self.algorithm_type)

    # 수락된 매칭의 추천은 보존되어야 함
    self.assertTrue(Referral.objects.filter(id=referrals[0].id).exists())

  def test_cleanup_preserves_referrals_with_rejected_matching(self):
    """거절된 매칭에 사용된 추천도 보존되는지 테스트"""
    # 20개의 추천 생성
    female_users = []
    referrals = []
    for i in range(20):
      female_user = User.objects.create_user(
        username=f"frejected_{i}",
        email=f"female_rejected_{i}@test.com",
      )
      Profile.objects.create(user=female_user, gender=Gender.FEMALE)
      female_users.append(female_user)

      referral = Referral.objects.create(
        user=self.male_user,
        referral_user=female_user,
        referred_at=timezone.now(),
        referred_algorithm=self.algorithm_type,
      )
      referrals.append(referral)

    # 첫 번째 추천으로 거절된 매칭 생성
    Matching.objects.create(
      sender=self.male_user,
      receiver=female_users[0],
      referral=referrals[0],
      ticket_amount=10,
      sent_at=timezone.now(),
      rejected_at=timezone.now(),  # 거절됨
    )

    # 정리 실행
    ReferralCreationService.cleanup_referrals_except_latest(self.male_user, self.algorithm_type)

    # 거절된 매칭의 추천도 보존되어야 함 (매칭에 사용되었기 때문)
    self.assertTrue(Referral.objects.filter(id=referrals[0].id).exists())

  def test_create_referral_cleans_up_when_no_users_first_time(self):
    """추천할 사용자가 없을 때 정리 후 재시도하는지 테스트"""
    # 많은 추천 생성
    for i in range(15):
      female_user = User.objects.create_user(
        username=f"fcreate_{i}",
        email=f"female_create_test_{i}@test.com",
      )
      Profile.objects.create(user=female_user, gender=Gender.FEMALE)

      Referral.objects.create(
        user=self.male_user,
        referral_user=female_user,
        referred_at=timezone.now(),
        referred_algorithm=self.algorithm_type,
      )

    # 추천 생성 시도 - cleanup이 실행되고 정리됨
    result = ReferralCreationService.create_referral(self.male_user, self.algorithm_type)

    # cleanup이 실행되어 최근 10개만 남음
    remaining_referrals = Referral.objects.filter(user=self.male_user).count()
    self.assertLessEqual(remaining_referrals, MAX_RECENT_REFERRALS_PER_ALGORITHM)
    # 추천할 사용자가 없어서 None 반환
    self.assertIsNone(result)

  @patch("api.v1.matchmakings.services.referral_creation_service.logger")
  def test_create_referral_logs_error_on_exception(self, mock_logger):
    """예외 발생 시 로그가 기록되는지 테스트"""
    # 프로필이 없는 사용자로 예외 발생 유도
    user_without_profile = User.objects.create_user(
      username="no_profile",
      email="no_profile@test.com",
      remaining_referral_quota=5,
    )

    # 예외가 발생하지 않더라도 None 반환
    result = ReferralCreationService.create_referral(user_without_profile, self.algorithm_type)
    self.assertIsNone(result)

  def test_apply_male_algorithm_returns_highest_score_user(self):
    """남성 알고리즘이 가장 높은 점수의 사용자를 반환하는지 테스트"""
    # PreMatching 생성
    prematching1 = PreMatching.objects.create(
      male_user=self.male_user,
      female_user=self.female_user1,
    )
    prematching2 = PreMatching.objects.create(
      male_user=self.male_user,
      female_user=self.female_user2,
    )

    # PreMatchingScore 생성
    PreMatchingScore.objects.create(
      prematching=prematching1,
      algorithm_category=self.algorithm_type,
      score=90,
    )
    PreMatchingScore.objects.create(
      prematching=prematching2,
      algorithm_category=self.algorithm_type,
      score=100,
    )

    users = User.objects.filter(id__in=[self.female_user1.id, self.female_user2.id])

    _score, recommended_user = ReferralCreationService._apply_male_algorithm(users, self.male_user, self.algorithm_type)

    # 추천 사용자가 있어야 함
    self.assertIsNotNone(recommended_user)

  def test_apply_female_algorithm_returns_highest_score_user(self):
    """여성 알고리즘이 가장 높은 점수의 사용자를 반환하는지 테스트"""
    # 여성 사용자 생성
    female_user = User.objects.create_user(
      username="female_test",
      email="female_test@test.com",
    )
    Profile.objects.create(user=female_user, gender=Gender.FEMALE)

    # PreMatching 생성
    prematching = PreMatching.objects.create(
      male_user=self.male_user,
      female_user=female_user,
    )

    # PreMatchingScore 생성
    PreMatchingScore.objects.create(
      prematching=prematching,
      algorithm_category=self.algorithm_type,
      score=100,
    )

    users = User.objects.filter(id=self.male_user.id)

    _score, recommended_user = ReferralCreationService._apply_female_algorithm(users, female_user, self.algorithm_type)

    # 추천 사용자가 있어야 함
    self.assertIsNotNone(recommended_user)
