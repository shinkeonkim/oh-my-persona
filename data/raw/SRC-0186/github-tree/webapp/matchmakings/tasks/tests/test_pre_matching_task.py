from datetime import timedelta
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone

from matchmakings.models import PreMatching, PreMatchingScore
from matchmakings.models.pre_matching import PreMatchingStatus
from matchmakings.tasks.pre_matching_task import (
  calculate_all_pre_matching_scores,
  calculate_pre_matching_score,
  reset_prematching_status,
  schedule_pre_matching_task,
)
from profiles.choices.profile_status_choices import ProfileStatusChoices
from profiles.models import Gender, Profile

User = get_user_model()


class ResetPrematchingStatusTest(TestCase):
  """reset_prematching_status 테스트"""

  def setUp(self):
    """테스트 데이터 설정"""
    self.male_user = User.objects.create_user(
        username="male_user",
        email="male@test.com",
    )
    self.female_user = User.objects.create_user(
        username="female_user",
        email="female@test.com",
    )
    Profile.objects.create(user=self.male_user, gender=Gender.MALE)
    Profile.objects.create(user=self.female_user, gender=Gender.FEMALE)

    self.prematching = PreMatching.objects.create(
        male_user=self.male_user,
        female_user=self.female_user,
        status=PreMatchingStatus.CALCULATING,
    )

  def test_reset_status_to_pending(self):
    """상태가 PENDING으로 리셋되는지 테스트"""
    reset_prematching_status(self.prematching.id)

    self.prematching.refresh_from_db()
    self.assertEqual(self.prematching.status, PreMatchingStatus.PENDING)

  def test_reset_nonexistent_prematching(self):
    """존재하지 않는 prematching을 리셋해도 에러가 발생하지 않는지 테스트"""
    # 존재하지 않는 ID로 호출
    reset_prematching_status(99999)
    # 에러 없이 실행되면 성공


class SchedulePreMatchingTaskTest(TestCase):
  """schedule_pre_matching_task 테스트"""

  def setUp(self):
    """테스트 데이터 설정"""
    self.male_user = User.objects.create_user(
        username="male_user",
        email="male@test.com",
    )
    Profile.objects.create(
        user=self.male_user,
        gender=Gender.MALE,
        status=ProfileStatusChoices.ACTIVE,
    )

    self.female_user1 = User.objects.create_user(
        username="female_user1",
        email="female1@test.com",
    )
    Profile.objects.create(
        user=self.female_user1,
        gender=Gender.FEMALE,
        status=ProfileStatusChoices.ACTIVE,
    )

    self.female_user2 = User.objects.create_user(
        username="female_user2",
        email="female2@test.com",
    )
    Profile.objects.create(
        user=self.female_user2,
        gender=Gender.FEMALE,
        status=ProfileStatusChoices.PENDING,
    )

  @patch("matchmakings.tasks.pre_matching_task.calculate_all_pre_matching_scores.delay")
  @patch("matchmakings.tasks.pre_matching_task.UserSajuChartService")
  def test_schedule_pre_matching_for_male_user(self, mock_saju_service, mock_calculate):
    """남성 사용자에 대한 pre_matching이 정상적으로 스케줄링되는지 테스트"""
    result = schedule_pre_matching_task(self.male_user.id)

    # PreMatching이 생성되었는지 확인
    prematchings = PreMatching.objects.filter(male_user=self.male_user)
    self.assertEqual(prematchings.count(), 2)  # female_user1, female_user2

    # 각 PreMatching에 대해 점수 계산 태스크가 호출되었는지 확인
    self.assertEqual(mock_calculate.call_count, 2)

    # 사주 차트 서비스가 호출되었는지 확인
    mock_saju_service.assert_called_once()

    # 성공 메시지 확인
    self.assertIn("PreMatchings calculated for user", result)

  @patch("matchmakings.tasks.pre_matching_task.calculate_all_pre_matching_scores.delay")
  @patch("matchmakings.tasks.pre_matching_task.UserSajuChartService")
  def test_schedule_pre_matching_for_female_user(self, mock_saju_service, mock_calculate):
    """여성 사용자에 대한 pre_matching이 정상적으로 스케줄링되는지 테스트"""
    result = schedule_pre_matching_task(self.female_user1.id)

    # PreMatching이 생성되었는지 확인 (male_user와 매칭)
    prematchings = PreMatching.objects.filter(female_user=self.female_user1)
    self.assertEqual(prematchings.count(), 1)

    # 점수 계산 태스크가 호출되었는지 확인
    mock_calculate.assert_called_once()

    # 성공 메시지 확인
    self.assertIn("PreMatchings calculated for user", result)

  def test_schedule_pre_matching_for_nonexistent_user(self):
    """존재하지 않는 사용자에 대한 처리 테스트"""
    result = schedule_pre_matching_task(99999)

    self.assertIn("User 99999 not found", result)

  def test_schedule_pre_matching_for_user_without_gender(self):
    """성별 정보가 없는 사용자에 대한 처리 테스트"""
    user_without_gender = User.objects.create_user(
        username="no_gender",
        email="no_gender@test.com",
    )

    result = schedule_pre_matching_task(user_without_gender.id)

    self.assertIn("has no gender information", result)

  def test_schedule_pre_matching_for_user_without_profile(self):
    """프로필이 없는 사용자에 대한 처리 테스트"""
    user_without_profile = User.objects.create_user(
        username="no_profile",
        email="no_profile@test.com",
    )

    result = schedule_pre_matching_task(user_without_profile.id)

    self.assertIn("has no gender information", result)

  @patch("matchmakings.tasks.pre_matching_task.calculate_all_pre_matching_scores.delay")
  @patch("matchmakings.tasks.pre_matching_task.UserSajuChartService")
  def test_skip_if_recent_task_exists(self, mock_saju_service, mock_calculate):
    """최근 10분 내에 실행된 태스크가 있으면 스킵하는지 테스트"""
    # 최근에 계산된 PreMatching 생성
    PreMatching.objects.create(
        male_user=self.male_user,
        female_user=self.female_user1,
        status=PreMatchingStatus.COMPLETED,
        last_calculated_at=timezone.now() - timedelta(minutes=5),
    )

    result = schedule_pre_matching_task(self.male_user.id)

    # 스킵되었는지 확인
    self.assertIn("Recent pre_matching task found", result)
    mock_calculate.assert_not_called()

  @patch("matchmakings.tasks.pre_matching_task.calculate_all_pre_matching_scores.delay")
  @patch("matchmakings.tasks.pre_matching_task.UserSajuChartService")
  def test_run_if_old_task_exists(self, mock_saju_service, mock_calculate):
    """10분 이상 지난 태스크는 다시 실행하는지 테스트"""
    # 오래된 PreMatching 생성
    PreMatching.objects.create(
        male_user=self.male_user,
        female_user=self.female_user1,
        status=PreMatchingStatus.COMPLETED,
        last_calculated_at=timezone.now() - timedelta(minutes=15),
    )

    result = schedule_pre_matching_task(self.male_user.id)

    # 실행되었는지 확인
    self.assertIn("PreMatchings calculated for user", result)
    self.assertGreater(mock_calculate.call_count, 0)

  @patch("matchmakings.tasks.pre_matching_task.calculate_all_pre_matching_scores.delay")
  @patch("matchmakings.tasks.pre_matching_task.UserSajuChartService")
  def test_exclude_inactive_profiles(self, mock_saju_service, mock_calculate):
    """ACTIVE 또는 PENDING이 아닌 프로필은 제외되는지 테스트"""
    # INACTIVE 프로필 생성
    inactive_female = User.objects.create_user(
        username="inactive_female",
        email="inactive@test.com",
    )
    Profile.objects.create(
        user=inactive_female,
        gender=Gender.FEMALE,
        status=ProfileStatusChoices.INACTIVE,
    )

    schedule_pre_matching_task(self.male_user.id)

    # inactive_female과의 PreMatching이 생성되지 않았는지 확인
    prematching_exists = PreMatching.objects.filter(
        male_user=self.male_user,
        female_user=inactive_female,
    ).exists()
    self.assertFalse(prematching_exists)

  @patch("matchmakings.tasks.pre_matching_task.calculate_all_pre_matching_scores.delay")
  @patch("matchmakings.tasks.pre_matching_task.UserSajuChartService")
  def test_exclude_self_from_matching(self, mock_saju_service, mock_calculate):
    """자기 자신은 매칭 대상에서 제외되는지 테스트"""
    schedule_pre_matching_task(self.male_user.id)

    # 자기 자신과의 PreMatching이 생성되지 않았는지 확인
    prematchings = PreMatching.objects.filter(
        male_user=self.male_user,
        female_user=self.male_user,
    )
    self.assertEqual(prematchings.count(), 0)

  @patch("matchmakings.tasks.pre_matching_task.calculate_all_pre_matching_scores.delay")
  @patch("matchmakings.tasks.pre_matching_task.UserSajuChartService")
  def test_get_or_create_prematching(self, mock_saju_service, mock_calculate):
    """이미 존재하는 PreMatching은 재사용되는지 테스트"""
    # 기존 PreMatching 생성
    existing_prematching = PreMatching.objects.create(
        male_user=self.male_user,
        female_user=self.female_user1,
        status=PreMatchingStatus.PENDING,
    )

    schedule_pre_matching_task(self.male_user.id)

    # PreMatching 개수가 증가하지 않았는지 확인
    prematchings = PreMatching.objects.filter(
        male_user=self.male_user,
        female_user=self.female_user1,
    )
    self.assertEqual(prematchings.count(), 1)

    # 기존 것과 동일한지 확인
    self.assertEqual(prematchings.first().id, existing_prematching.id)


@override_settings(MATCHING_ALGORITHM_NAMES=["TestAlgorithm1", "TestAlgorithm2"])
class CalculateAllPreMatchingScoresTest(TestCase):
  """calculate_all_pre_matching_scores 테스트"""

  def setUp(self):
    """테스트 데이터 설정"""
    self.male_user = User.objects.create_user(
        username="male_user",
        email="male@test.com",
    )
    self.female_user = User.objects.create_user(
        username="female_user",
        email="female@test.com",
    )
    Profile.objects.create(user=self.male_user, gender=Gender.MALE)
    Profile.objects.create(user=self.female_user, gender=Gender.FEMALE)

    self.prematching = PreMatching.objects.create(
        male_user=self.male_user,
        female_user=self.female_user,
        status=PreMatchingStatus.PENDING,
    )

  @patch("matchmakings.tasks.pre_matching_task.AlgorithmFactory.create_algorithm")
  def test_calculate_all_scores_success(self, mock_create_algorithm):
    """모든 알고리즘으로 점수가 계산되는지 테스트"""
    # Mock 알고리즘 설정
    mock_algorithm1 = Mock()
    mock_algorithm1.run.return_value = 85
    mock_algorithm2 = Mock()
    mock_algorithm2.run.return_value = 90

    mock_create_algorithm.side_effect = [mock_algorithm1, mock_algorithm2]

    # 태스크 실행
    result = calculate_all_pre_matching_scores(self.prematching.id)

    # PreMatching 상태가 COMPLETED로 변경되었는지 확인
    self.prematching.refresh_from_db()
    self.assertEqual(self.prematching.status, PreMatchingStatus.COMPLETED)
    self.assertIsNotNone(self.prematching.last_calculated_at)

    # PreMatchingScore가 생성되었는지 확인
    scores = PreMatchingScore.objects.filter(prematching=self.prematching)
    self.assertEqual(scores.count(), 2)

    # 각 알고리즘에 대한 점수 확인
    score1 = scores.get(algorithm_category="TestAlgorithm1")
    score2 = scores.get(algorithm_category="TestAlgorithm2")
    self.assertEqual(score1.score, 85)
    self.assertEqual(score2.score, 90)

    # 결과 메시지 확인
    self.assertIn("TestAlgorithm1: 85", result)
    self.assertIn("TestAlgorithm2: 90", result)

  @patch("matchmakings.tasks.pre_matching_task.AlgorithmFactory.create_algorithm")
  def test_calculate_scores_updates_existing_scores(self, mock_create_algorithm):
    """이미 존재하는 점수를 업데이트하는지 테스트"""
    # 기존 점수 생성
    PreMatchingScore.objects.create(
        prematching=self.prematching,
        algorithm_category="TestAlgorithm1",
        score=50,
    )

    # Mock 알고리즘 설정
    mock_algorithm = Mock()
    mock_algorithm.run.return_value = 85

    mock_create_algorithm.return_value = mock_algorithm

    # 태스크 실행
    calculate_all_pre_matching_scores(self.prematching.id)

    # 점수가 업데이트되었는지 확인
    score = PreMatchingScore.objects.get(
        prematching=self.prematching,
        algorithm_category="TestAlgorithm1",
    )
    self.assertEqual(score.score, 85)

  @patch("matchmakings.tasks.pre_matching_task.AlgorithmFactory.create_algorithm")
  def test_calculate_scores_continues_on_algorithm_error(self, mock_create_algorithm):
    """개별 알고리즘 에러 시에도 다른 알고리즘은 계속 실행되는지 테스트"""
    # Mock 알고리즘 설정 (첫 번째는 에러, 두 번째는 성공)
    mock_algorithm1 = Mock()
    mock_algorithm1.run.side_effect = Exception("Algorithm error")
    mock_algorithm2 = Mock()
    mock_algorithm2.run.return_value = 90

    mock_create_algorithm.side_effect = [mock_algorithm1, mock_algorithm2]

    # 태스크 실행
    result = calculate_all_pre_matching_scores(self.prematching.id)

    # PreMatching 상태가 COMPLETED로 변경되었는지 확인
    self.prematching.refresh_from_db()
    self.assertEqual(self.prematching.status, PreMatchingStatus.COMPLETED)

    # 성공한 알고리즘의 점수만 생성되었는지 확인
    scores = PreMatchingScore.objects.filter(prematching=self.prematching)
    self.assertEqual(scores.count(), 1)
    self.assertEqual(scores.first().algorithm_category, "TestAlgorithm2")
    self.assertEqual(scores.first().score, 90)

    # 에러 메시지가 포함되었는지 확인
    self.assertIn("ERROR", result)
    self.assertIn("TestAlgorithm2: 90", result)

  def test_calculate_scores_for_nonexistent_prematching(self):
    """존재하지 않는 PreMatching에 대한 처리 테스트"""
    result = calculate_all_pre_matching_scores(99999)

    self.assertIn("PreMatching 99999 not found", result)

  @patch("matchmakings.tasks.pre_matching_task.AlgorithmFactory.create_algorithm")
  def test_calculate_scores_sets_status_to_calculating(self, mock_create_algorithm):
    """점수 계산 시작 시 상태가 CALCULATING으로 변경되는지 테스트"""
    mock_algorithm = Mock()
    mock_algorithm.run.return_value = 85
    mock_create_algorithm.return_value = mock_algorithm

    # 상태 변경 확인을 위해 트랜잭션 내부 동작을 시뮬레이션
    calculate_all_pre_matching_scores(self.prematching.id)

    # 최종 상태가 COMPLETED인지 확인
    self.prematching.refresh_from_db()
    self.assertEqual(self.prematching.status, PreMatchingStatus.COMPLETED)

  @patch("matchmakings.tasks.pre_matching_task.AlgorithmFactory.get_available_algorithms")
  @patch("matchmakings.tasks.pre_matching_task.reset_prematching_status")
  def test_calculate_scores_resets_status_on_error(self, mock_reset, mock_get_algorithms):
    """에러 발생 시 상태가 PENDING으로 리셋되는지 테스트"""
    # get_available_algorithms에서 에러 발생시키기 (트랜잭션 내부에서 발생)
    mock_get_algorithms.side_effect = Exception("Fatal error")

    # 태스크 실행
    result = calculate_all_pre_matching_scores(self.prematching.id)

    # reset 함수가 호출되었는지 확인
    mock_reset.assert_called_once_with(self.prematching.id)

    # 에러 메시지 확인
    self.assertIn("Error calculating scores", result)


@override_settings(MATCHING_ALGORITHM_NAMES=["TestAlgorithm"])
class CalculatePreMatchingScoreTest(TestCase):
  """calculate_pre_matching_score 테스트"""

  def setUp(self):
    """테스트 데이터 설정"""
    self.male_user = User.objects.create_user(
        username="male_user",
        email="male@test.com",
    )
    self.female_user = User.objects.create_user(
        username="female_user",
        email="female@test.com",
    )
    Profile.objects.create(user=self.male_user, gender=Gender.MALE)
    Profile.objects.create(user=self.female_user, gender=Gender.FEMALE)

    self.prematching = PreMatching.objects.create(
        male_user=self.male_user,
        female_user=self.female_user,
        status=PreMatchingStatus.PENDING,
    )

  @patch("matchmakings.tasks.pre_matching_task.AlgorithmFactory.create_algorithm")
  def test_calculate_single_algorithm_score_success(self, mock_create_algorithm):
    """단일 알고리즘으로 점수가 계산되는지 테스트"""
    # Mock 알고리즘 설정
    mock_algorithm = Mock()
    mock_algorithm.run.return_value = 85
    mock_create_algorithm.return_value = mock_algorithm

    # 태스크 실행
    result = calculate_pre_matching_score(self.prematching.id, "TestAlgorithm")

    # PreMatching 상태가 COMPLETED로 변경되었는지 확인
    self.prematching.refresh_from_db()
    self.assertEqual(self.prematching.status, PreMatchingStatus.COMPLETED)
    self.assertIsNotNone(self.prematching.last_calculated_at)

    # PreMatchingScore가 생성되었는지 확인
    score = PreMatchingScore.objects.get(
        prematching=self.prematching,
        algorithm_category="TestAlgorithm",
    )
    self.assertEqual(score.score, 85)

    # 결과 메시지 확인
    self.assertIn("Calculated score 85", result)
    self.assertIn("TestAlgorithm", result)

  @patch("matchmakings.tasks.pre_matching_task.AlgorithmFactory.create_algorithm")
  def test_calculate_single_score_updates_existing(self, mock_create_algorithm):
    """이미 존재하는 점수를 업데이트하는지 테스트"""
    # 기존 점수 생성
    PreMatchingScore.objects.create(
        prematching=self.prematching,
        algorithm_category="TestAlgorithm",
        score=50,
    )

    # Mock 알고리즘 설정
    mock_algorithm = Mock()
    mock_algorithm.run.return_value = 85
    mock_create_algorithm.return_value = mock_algorithm

    # 태스크 실행
    calculate_pre_matching_score(self.prematching.id, "TestAlgorithm")

    # 점수가 업데이트되었는지 확인
    score = PreMatchingScore.objects.get(
        prematching=self.prematching,
        algorithm_category="TestAlgorithm",
    )
    self.assertEqual(score.score, 85)

  def test_calculate_single_score_for_nonexistent_prematching(self):
    """존재하지 않는 PreMatching에 대한 처리 테스트"""
    result = calculate_pre_matching_score(99999, "TestAlgorithm")

    self.assertIn("PreMatching 99999 not found", result)

  @patch("matchmakings.tasks.pre_matching_task.AlgorithmFactory.create_algorithm")
  @patch("matchmakings.tasks.pre_matching_task.reset_prematching_status")
  def test_calculate_single_score_resets_status_on_error(self, mock_reset, mock_create_algorithm):
    """에러 발생 시 상태가 PENDING으로 리셋되는지 테스트"""
    # 에러 발생시키기
    mock_create_algorithm.side_effect = Exception("Algorithm error")

    # 태스크 실행
    result = calculate_pre_matching_score(self.prematching.id, "TestAlgorithm")

    # reset 함수가 호출되었는지 확인
    mock_reset.assert_called_once_with(self.prematching.id)

    # 에러 메시지 확인
    self.assertIn("Error calculating score", result)

  @patch("matchmakings.tasks.pre_matching_task.AlgorithmFactory.create_algorithm")
  def test_calculate_single_score_sets_last_calculated_at(self, mock_create_algorithm):
    """점수 계산 후 last_calculated_at이 설정되는지 테스트"""
    mock_algorithm = Mock()
    mock_algorithm.run.return_value = 85
    mock_create_algorithm.return_value = mock_algorithm

    before_calculation = timezone.now()

    # 태스크 실행
    calculate_pre_matching_score(self.prematching.id, "TestAlgorithm")

    after_calculation = timezone.now()

    # last_calculated_at이 적절한 시간대에 설정되었는지 확인
    self.prematching.refresh_from_db()
    self.assertIsNotNone(self.prematching.last_calculated_at)
    self.assertGreaterEqual(self.prematching.last_calculated_at, before_calculation)
    self.assertLessEqual(self.prematching.last_calculated_at, after_calculation)

  @patch("matchmakings.tasks.pre_matching_task.AlgorithmFactory.create_algorithm")
  def test_calculate_single_score_uses_select_for_update(self, mock_create_algorithm):
    """select_for_update를 사용하여 동시성 제어가 되는지 테스트"""
    mock_algorithm = Mock()
    mock_algorithm.run.return_value = 85
    mock_create_algorithm.return_value = mock_algorithm

    # 정상적으로 실행되는지 확인
    result = calculate_pre_matching_score(self.prematching.id, "TestAlgorithm")

    self.assertIn("Calculated score", result)
    self.prematching.refresh_from_db()
    self.assertEqual(self.prematching.status, PreMatchingStatus.COMPLETED)
