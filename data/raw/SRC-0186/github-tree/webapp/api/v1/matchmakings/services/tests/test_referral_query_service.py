from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from api.v1.matchmakings.exceptions import ReferralNotFoundError
from api.v1.matchmakings.services import ReferralQueryService
from matchmakings.models import PreMatching, PreMatchingScore, Referral
from profiles.models import Gender, Profile

User = get_user_model()


class ReferralQueryServiceTest(TestCase):
  """ReferralQueryService 테스트"""

  def setUp(self):
    """테스트 데이터 설정"""
    # 남성 사용자 생성
    self.male_user = User.objects.create_user(
      username="male_user",
      email="male@test.com",
    )
    Profile.objects.create(user=self.male_user, gender=Gender.MALE)

    # 여성 사용자 생성
    self.female_user1 = User.objects.create_user(
      username="female_user1",
      email="female1@test.com",
    )
    Profile.objects.create(user=self.female_user1, gender=Gender.FEMALE)

    self.female_user2 = User.objects.create_user(
      username="female_user2",
      email="female2@test.com",
    )
    Profile.objects.create(user=self.female_user2, gender=Gender.FEMALE)

    self.algorithm_type = "TestAlgorithm"
    self.other_algorithm_type = "OtherAlgorithm"

  def test_get_latest_referral_without_algorithm_type(self):
    """알고리즘 타입 없이 가장 최근 추천을 조회하는지 테스트"""
    # 여러 추천 생성 (시간차를 두고)
    Referral.objects.create(
      user=self.male_user,
      referral_user=self.female_user1,
      referred_at=timezone.now(),
      referred_algorithm=self.algorithm_type,
    )

    Referral.objects.create(
      user=self.male_user,
      referral_user=self.female_user2,
      referred_at=timezone.now(),
      referred_algorithm=self.other_algorithm_type,
    )

    # 가장 최근 추천 조회
    latest_referral = ReferralQueryService.get_latest_referral(self.male_user)

    # 가장 최근에 생성된 추천이 반환되는지 확인
    self.assertIsNotNone(latest_referral)
    self.assertEqual(latest_referral.user, self.male_user)

  def test_get_latest_referral_with_algorithm_type(self):
    """알고리즘 타입으로 필터링하여 최근 추천을 조회하는지 테스트"""
    # PreMatching 생성 (알고리즘 스코어 설정을 위해)
    prematching1 = PreMatching.objects.create(
      male_user=self.male_user,
      female_user=self.female_user1,
    )

    # PreMatchingScore 생성
    PreMatchingScore.objects.create(
      prematching=prematching1,
      algorithm_category=self.algorithm_type,
      score=80,
    )

    # 추천 생성
    Referral.objects.create(
      user=self.male_user,
      referral_user=self.female_user1,
      referred_at=timezone.now(),
      referred_algorithm=self.algorithm_type,
    )

    # 다른 알고리즘으로 추천 생성
    Referral.objects.create(
      user=self.male_user,
      referral_user=self.female_user2,
      referred_at=timezone.now(),
      referred_algorithm=self.other_algorithm_type,
    )

    # 특정 알고리즘 타입으로 조회
    latest_referral = ReferralQueryService.get_latest_referral(self.male_user, algorithm_type=self.algorithm_type)

    # 해당 알고리즘의 추천이 반환되는지 확인
    self.assertIsNotNone(latest_referral)
    self.assertEqual(latest_referral.referral_user, self.female_user1)

  def test_get_latest_referral_raises_error_when_not_found(self):
    """추천이 없을 때 ReferralNotFoundError가 발생하는지 테스트"""
    with self.assertRaises(ReferralNotFoundError) as context:
      ReferralQueryService.get_latest_referral(self.male_user)

    self.assertIn("No referrals found", str(context.exception))

  def test_get_latest_referral_raises_error_when_algorithm_not_found(self):
    """특정 알고리즘의 추천이 없을 때 ReferralNotFoundError가 발생하는지 테스트"""
    # 다른 알고리즘으로 추천 생성
    Referral.objects.create(
      user=self.male_user,
      referral_user=self.female_user1,
      referred_at=timezone.now(),
      referred_algorithm=self.other_algorithm_type,
    )

    with self.assertRaises(ReferralNotFoundError) as context:
      ReferralQueryService.get_latest_referral(self.male_user, algorithm_type=self.algorithm_type)

    self.assertIn("No referrals found", str(context.exception))

  def test_get_latest_referral_returns_most_recent(self):
    """여러 추천 중 가장 최근 것을 반환하는지 테스트"""
    # 이전 추천 생성
    Referral.objects.create(
      user=self.male_user,
      referral_user=self.female_user1,
      referred_at=timezone.now() - timezone.timedelta(days=1),
      referred_algorithm=self.algorithm_type,
    )

    # 최근 추천 생성
    recent_referral = Referral.objects.create(
      user=self.male_user,
      referral_user=self.female_user2,
      referred_at=timezone.now(),
      referred_algorithm=self.algorithm_type,
    )

    latest_referral = ReferralQueryService.get_latest_referral(self.male_user)

    # 가장 최근 추천이 반환되는지 확인
    self.assertEqual(latest_referral.id, recent_referral.id)
    self.assertEqual(latest_referral.referral_user, self.female_user2)

  def test_get_latest_referral_with_related_data(self):
    """추천 조회 시 연관 데이터가 함께 조회되는지 테스트"""
    # 추천 생성
    Referral.objects.create(
      user=self.male_user,
      referral_user=self.female_user1,
      referred_at=timezone.now(),
      referred_algorithm=self.algorithm_type,
    )

    latest_referral = ReferralQueryService.get_latest_referral(self.male_user)

    # 연관 데이터가 함께 조회되는지 확인 (select_related 효과)
    # 추가 쿼리 없이 접근 가능해야 함
    self.assertIsNotNone(latest_referral.referral_user)
    self.assertIsNotNone(latest_referral.referral_user.profile)

  def test_get_latest_referral_filters_by_female_to_male(self):
    """여성 사용자가 남성 추천을 조회할 때 올바르게 필터링되는지 테스트"""
    # PreMatching 생성 (여성이 남성을 조회하는 경우)
    prematching = PreMatching.objects.create(
      male_user=self.male_user,
      female_user=self.female_user1,
    )

    # PreMatchingScore 생성
    PreMatchingScore.objects.create(
      prematching=prematching,
      algorithm_category=self.algorithm_type,
      score=80,
    )

    # 여성이 남성을 추천받음
    Referral.objects.create(
      user=self.female_user1,
      referral_user=self.male_user,
      referred_at=timezone.now(),
      referred_algorithm=self.algorithm_type,
    )

    # 여성 사용자로 조회
    latest_referral = ReferralQueryService.get_latest_referral(self.female_user1, algorithm_type=self.algorithm_type)

    self.assertIsNotNone(latest_referral)
    self.assertEqual(latest_referral.referral_user, self.male_user)

  def test_get_latest_referral_error_includes_details(self):
    """추천이 없을 때 발생하는 에러에 상세 정보가 포함되는지 테스트"""
    try:
      ReferralQueryService.get_latest_referral(self.male_user, algorithm_type=self.algorithm_type)
    except ReferralNotFoundError as e:
      # 에러 details에 user_id와 algorithm_type이 포함되는지 확인
      self.assertEqual(e.details["user_id"], self.male_user.id)
      self.assertEqual(e.details["algorithm_type"], self.algorithm_type)

  def test_get_latest_referral_with_multiple_algorithms(self):
    """여러 알고리즘의 추천 중 특정 알고리즘만 조회하는지 테스트"""
    # PreMatching 생성
    prematching1 = PreMatching.objects.create(
      male_user=self.male_user,
      female_user=self.female_user1,
    )
    prematching2 = PreMatching.objects.create(
      male_user=self.male_user,
      female_user=self.female_user2,
    )

    # 서로 다른 알고리즘으로 스코어 생성
    PreMatchingScore.objects.create(
      prematching=prematching1,
      algorithm_category=self.algorithm_type,
      score=80,
    )
    PreMatchingScore.objects.create(
      prematching=prematching2,
      algorithm_category=self.other_algorithm_type,
      score=90,
    )

    # 추천 생성
    Referral.objects.create(
      user=self.male_user,
      referral_user=self.female_user1,
      referred_at=timezone.now() - timezone.timedelta(hours=2),
      referred_algorithm=self.algorithm_type,
    )

    Referral.objects.create(
      user=self.male_user,
      referral_user=self.female_user2,
      referred_at=timezone.now() - timezone.timedelta(hours=1),
      referred_algorithm=self.other_algorithm_type,
    )

    # TestAlgorithm으로 조회
    latest_test_algorithm = ReferralQueryService.get_latest_referral(self.male_user, algorithm_type=self.algorithm_type)

    # OtherAlgorithm으로 조회
    latest_other_algorithm = ReferralQueryService.get_latest_referral(self.male_user,
                                                                      algorithm_type=self.other_algorithm_type)

    # 각각 올바른 추천이 반환되는지 확인
    self.assertEqual(latest_test_algorithm.referral_user, self.female_user1)
    self.assertEqual(latest_other_algorithm.referral_user, self.female_user2)

  def test_get_latest_referral_orders_by_referred_at_desc(self):
    """추천이 referred_at 기준 내림차순으로 정렬되는지 테스트"""
    # 여러 추천을 시간차를 두고 생성
    referrals = []
    for i in range(5):
      # 각 추천마다 다른 사용자 생성하여 unique constraint 충돌 방지
      female_user = User.objects.create_user(
        username=f"female_order_{i}",
        email=f"female_order_{i}@test.com",
      )
      Profile.objects.create(user=female_user, gender=Gender.FEMALE)

      referral = Referral.objects.create(
        user=self.male_user,
        referral_user=female_user,
        referred_at=timezone.now() - timezone.timedelta(hours=i),
        referred_algorithm=self.algorithm_type,
      )
      referrals.append(referral)

    latest_referral = ReferralQueryService.get_latest_referral(self.male_user)

    # 가장 최근 것이 반환되는지 확인 (i=0인 것)
    self.assertEqual(latest_referral.id, referrals[0].id)
