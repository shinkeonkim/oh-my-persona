from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from matchmakings.models import PreMatching, PreMatchingStatus
from profiles.models import Gender, Profile

User = get_user_model()


class PreMatchingModelTest(TestCase):
  """PreMatching 모델 테스트"""

  def setUp(self):
    """테스트 데이터 설정"""
    # 남성 사용자 생성
    self.male_user = User.objects.create_user(
      username="male_user",
      email="male@test.com",
    )
    Profile.objects.create(user=self.male_user, gender=Gender.MALE)

    # 여성 사용자 생성
    self.female_user = User.objects.create_user(
      username="female_user",
      email="female@test.com",
    )
    Profile.objects.create(user=self.female_user, gender=Gender.FEMALE)

  def test_create_pre_matching_success(self):
    """PreMatching이 정상적으로 생성되는지 테스트"""
    pre_matching = PreMatching.objects.create(
      male_user=self.male_user,
      female_user=self.female_user,
    )

    self.assertIsNotNone(pre_matching.id)
    self.assertEqual(pre_matching.male_user, self.male_user)
    self.assertEqual(pre_matching.female_user, self.female_user)
    self.assertEqual(pre_matching.status, PreMatchingStatus.PENDING)
    self.assertEqual(pre_matching.compatibility_score, 0)
    self.assertIsNone(pre_matching.last_calculated_at)
    self.assertIsNone(pre_matching.matching_reason)

  def test_pre_matching_default_status(self):
    """PreMatching의 기본 상태가 PENDING인지 테스트"""
    pre_matching = PreMatching.objects.create(
      male_user=self.male_user,
      female_user=self.female_user,
    )

    self.assertEqual(pre_matching.status, PreMatchingStatus.PENDING)

  def test_pre_matching_status_update(self):
    """PreMatching 상태를 업데이트할 수 있는지 테스트"""
    pre_matching = PreMatching.objects.create(
      male_user=self.male_user,
      female_user=self.female_user,
    )

    pre_matching.status = PreMatchingStatus.CALCULATING
    pre_matching.save()

    pre_matching.refresh_from_db()
    self.assertEqual(pre_matching.status, PreMatchingStatus.CALCULATING)

  def test_pre_matching_all_statuses(self):
    """모든 PreMatching 상태가 올바르게 설정되는지 테스트"""
    pre_matching = PreMatching.objects.create(
      male_user=self.male_user,
      female_user=self.female_user,
    )

    # PENDING
    self.assertEqual(pre_matching.status, PreMatchingStatus.PENDING)

    # CALCULATING
    pre_matching.status = PreMatchingStatus.CALCULATING
    pre_matching.save()
    pre_matching.refresh_from_db()
    self.assertEqual(pre_matching.status, PreMatchingStatus.CALCULATING)

    # COMPLETED
    pre_matching.status = PreMatchingStatus.COMPLETED
    pre_matching.save()
    pre_matching.refresh_from_db()
    self.assertEqual(pre_matching.status, PreMatchingStatus.COMPLETED)

    # RECOMMENDED
    pre_matching.status = PreMatchingStatus.RECOMMENDED
    pre_matching.save()
    pre_matching.refresh_from_db()
    self.assertEqual(pre_matching.status, PreMatchingStatus.RECOMMENDED)

  def test_pre_matching_unique_constraint(self):
    """동일한 male_user와 female_user로 중복 생성이 불가능한지 테스트"""
    PreMatching.objects.create(
      male_user=self.male_user,
      female_user=self.female_user,
    )

    # 같은 male_user와 female_user로 다시 생성 시도
    with self.assertRaises(Exception):  # IntegrityError
      PreMatching.objects.create(
        male_user=self.male_user,
        female_user=self.female_user,
      )

  def test_pre_matching_compatibility_score(self):
    """PreMatching의 궁합 점수를 설정할 수 있는지 테스트"""
    pre_matching = PreMatching.objects.create(
      male_user=self.male_user,
      female_user=self.female_user,
      compatibility_score=85,
    )

    self.assertEqual(pre_matching.compatibility_score, 85)

  def test_pre_matching_matching_reason(self):
    """PreMatching의 매칭 사유를 설정할 수 있는지 테스트"""
    reason = "두 사람은 비슷한 가치관을 가지고 있습니다."
    pre_matching = PreMatching.objects.create(
      male_user=self.male_user,
      female_user=self.female_user,
      matching_reason=reason,
    )

    self.assertEqual(pre_matching.matching_reason, reason)

  def test_pre_matching_last_calculated_at(self):
    """PreMatching의 마지막 계산 시간을 설정할 수 있는지 테스트"""
    now = timezone.now()
    pre_matching = PreMatching.objects.create(
      male_user=self.male_user,
      female_user=self.female_user,
      last_calculated_at=now,
    )

    self.assertEqual(pre_matching.last_calculated_at, now)

  def test_pre_matching_cascade_delete_on_male_user_delete(self):
    """male_user가 삭제되면 PreMatching도 삭제되는지 테스트"""
    pre_matching = PreMatching.objects.create(
      male_user=self.male_user,
      female_user=self.female_user,
    )

    pre_matching_id = pre_matching.id
    self.male_user.delete()

    self.assertFalse(PreMatching.objects.filter(id=pre_matching_id).exists())

  def test_pre_matching_cascade_delete_on_female_user_delete(self):
    """female_user가 삭제되면 PreMatching도 삭제되는지 테스트"""
    pre_matching = PreMatching.objects.create(
      male_user=self.male_user,
      female_user=self.female_user,
    )

    pre_matching_id = pre_matching.id
    self.female_user.delete()

    self.assertFalse(PreMatching.objects.filter(id=pre_matching_id).exists())

  def test_multiple_pre_matchings_for_same_male_user(self):
    """동일한 male_user에 대해 여러 PreMatching이 생성될 수 있는지 테스트"""
    another_female = User.objects.create_user(
      username="another_female",
      email="another_female@test.com",
    )
    Profile.objects.create(user=another_female, gender=Gender.FEMALE)

    pre_matching1 = PreMatching.objects.create(
      male_user=self.male_user,
      female_user=self.female_user,
    )

    pre_matching2 = PreMatching.objects.create(
      male_user=self.male_user,
      female_user=another_female,
    )

    self.assertNotEqual(pre_matching1.id, pre_matching2.id)
    self.assertEqual(PreMatching.objects.filter(male_user=self.male_user).count(), 2)

  def test_multiple_pre_matchings_for_same_female_user(self):
    """동일한 female_user에 대해 여러 PreMatching이 생성될 수 있는지 테스트"""
    another_male = User.objects.create_user(
      username="another_male",
      email="another_male@test.com",
    )
    Profile.objects.create(user=another_male, gender=Gender.MALE)

    pre_matching1 = PreMatching.objects.create(
      male_user=self.male_user,
      female_user=self.female_user,
    )

    pre_matching2 = PreMatching.objects.create(
      male_user=another_male,
      female_user=self.female_user,
    )

    self.assertNotEqual(pre_matching1.id, pre_matching2.id)
    self.assertEqual(PreMatching.objects.filter(female_user=self.female_user).count(), 2)

  def test_pre_matching_related_name_male_pre_matchings(self):
    """male_user의 related_name이 올바르게 동작하는지 테스트"""
    pre_matching = PreMatching.objects.create(
      male_user=self.male_user,
      female_user=self.female_user,
    )

    male_pre_matchings = self.male_user.male_pre_matchings.all()
    self.assertEqual(male_pre_matchings.count(), 1)
    self.assertIn(pre_matching, male_pre_matchings)

  def test_pre_matching_related_name_female_pre_matchings(self):
    """female_user의 related_name이 올바르게 동작하는지 테스트"""
    pre_matching = PreMatching.objects.create(
      male_user=self.male_user,
      female_user=self.female_user,
    )

    female_pre_matchings = self.female_user.female_pre_matchings.all()
    self.assertEqual(female_pre_matchings.count(), 1)
    self.assertIn(pre_matching, female_pre_matchings)

  def test_pre_matching_default_compatibility_score_is_zero(self):
    """PreMatching의 기본 궁합 점수가 0인지 테스트"""
    pre_matching = PreMatching.objects.create(
      male_user=self.male_user,
      female_user=self.female_user,
    )

    self.assertEqual(pre_matching.compatibility_score, 0)

  def test_pre_matching_update_compatibility_score(self):
    """PreMatching의 궁합 점수를 업데이트할 수 있는지 테스트"""
    pre_matching = PreMatching.objects.create(
      male_user=self.male_user,
      female_user=self.female_user,
    )

    pre_matching.compatibility_score = 95
    pre_matching.save()

    pre_matching.refresh_from_db()
    self.assertEqual(pre_matching.compatibility_score, 95)

  def test_pre_matching_update_last_calculated_at(self):
    """PreMatching의 마지막 계산 시간을 업데이트할 수 있는지 테스트"""
    pre_matching = PreMatching.objects.create(
      male_user=self.male_user,
      female_user=self.female_user,
    )

    now = timezone.now()
    pre_matching.last_calculated_at = now
    pre_matching.save()

    pre_matching.refresh_from_db()
    self.assertIsNotNone(pre_matching.last_calculated_at)
    # timezone.now()와 정확히 같지 않을 수 있으므로 범위로 확인
    self.assertLess((timezone.now() - pre_matching.last_calculated_at).total_seconds(), 1)
