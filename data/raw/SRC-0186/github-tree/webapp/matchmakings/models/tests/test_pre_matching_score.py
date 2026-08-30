from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from matchmakings.models import PreMatching, PreMatchingScore
from profiles.models import Gender, Profile

User = get_user_model()


@override_settings(MATCHING_ALGORITHM_NAMES=["Algorithm1", "Algorithm2", "Algorithm3"])
class PreMatchingScoreModelTest(TestCase):
    """PreMatchingScore 모델 테스트"""

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

        # PreMatching 생성
        self.pre_matching = PreMatching.objects.create(
            male_user=self.male_user,
            female_user=self.female_user,
        )

    def test_create_pre_matching_score_success(self):
        """PreMatchingScore가 정상적으로 생성되는지 테스트"""
        score = PreMatchingScore.objects.create(
            prematching=self.pre_matching,
            algorithm_category="Algorithm1",
            score=85,
        )

        self.assertIsNotNone(score.id)
        self.assertEqual(score.prematching, self.pre_matching)
        self.assertEqual(score.algorithm_category, "Algorithm1")
        self.assertEqual(score.score, 85)

    def test_pre_matching_score_default_score_is_zero(self):
        """PreMatchingScore의 기본 점수가 0인지 테스트"""
        score = PreMatchingScore.objects.create(
            prematching=self.pre_matching,
            algorithm_category="Algorithm1",
        )

        self.assertEqual(score.score, 0)

    def test_pre_matching_score_unique_constraint(self):
        """동일한 prematching과 algorithm_category로 중복 생성이 불가능한지 테스트"""
        PreMatchingScore.objects.create(
            prematching=self.pre_matching,
            algorithm_category="Algorithm1",
            score=85,
        )

        # 같은 prematching과 algorithm_category로 다시 생성 시도
        with self.assertRaises(Exception):  # IntegrityError
            PreMatchingScore.objects.create(
                prematching=self.pre_matching,
                algorithm_category="Algorithm1",
                score=90,
            )

    def test_multiple_scores_for_different_algorithms(self):
        """동일한 prematching에 대해 여러 알고리즘의 점수를 생성할 수 있는지 테스트"""
        score1 = PreMatchingScore.objects.create(
            prematching=self.pre_matching,
            algorithm_category="Algorithm1",
            score=85,
        )

        score2 = PreMatchingScore.objects.create(
            prematching=self.pre_matching,
            algorithm_category="Algorithm2",
            score=90,
        )

        score3 = PreMatchingScore.objects.create(
            prematching=self.pre_matching,
            algorithm_category="Algorithm3",
            score=78,
        )

        scores = PreMatchingScore.objects.filter(prematching=self.pre_matching)
        self.assertEqual(scores.count(), 3)
        self.assertIn(score1, scores)
        self.assertIn(score2, scores)
        self.assertIn(score3, scores)

    def test_pre_matching_score_update(self):
        """PreMatchingScore를 업데이트할 수 있는지 테스트"""
        score = PreMatchingScore.objects.create(
            prematching=self.pre_matching,
            algorithm_category="Algorithm1",
            score=85,
        )

        score.score = 95
        score.save()

        score.refresh_from_db()
        self.assertEqual(score.score, 95)

    def test_pre_matching_score_cascade_delete_on_prematching_delete(self):
        """prematching이 삭제되면 PreMatchingScore도 삭제되는지 테스트"""
        score = PreMatchingScore.objects.create(
            prematching=self.pre_matching,
            algorithm_category="Algorithm1",
            score=85,
        )

        score_id = score.id
        self.pre_matching.delete()

        self.assertFalse(PreMatchingScore.objects.filter(id=score_id).exists())

    def test_pre_matching_score_related_name(self):
        """PreMatching의 related_name pre_matching_scores가 올바르게 동작하는지 테스트"""
        score1 = PreMatchingScore.objects.create(
            prematching=self.pre_matching,
            algorithm_category="Algorithm1",
            score=85,
        )

        score2 = PreMatchingScore.objects.create(
            prematching=self.pre_matching,
            algorithm_category="Algorithm2",
            score=90,
        )

        scores = self.pre_matching.pre_matching_scores.all()
        self.assertEqual(scores.count(), 2)
        self.assertIn(score1, scores)
        self.assertIn(score2, scores)

    def test_pre_matching_score_filter_by_algorithm(self):
        """알고리즘 카테고리로 점수를 필터링할 수 있는지 테스트"""
        PreMatchingScore.objects.create(
            prematching=self.pre_matching,
            algorithm_category="Algorithm1",
            score=85,
        )

        PreMatchingScore.objects.create(
            prematching=self.pre_matching,
            algorithm_category="Algorithm2",
            score=90,
        )

        algorithm1_scores = PreMatchingScore.objects.filter(algorithm_category="Algorithm1")
        self.assertEqual(algorithm1_scores.count(), 1)
        self.assertEqual(algorithm1_scores.first().score, 85)

    def test_pre_matching_score_order_by_score(self):
        """점수로 정렬할 수 있는지 테스트"""
        score1 = PreMatchingScore.objects.create(
            prematching=self.pre_matching,
            algorithm_category="Algorithm1",
            score=70,
        )

        score2 = PreMatchingScore.objects.create(
            prematching=self.pre_matching,
            algorithm_category="Algorithm2",
            score=90,
        )

        score3 = PreMatchingScore.objects.create(
            prematching=self.pre_matching,
            algorithm_category="Algorithm3",
            score=80,
        )

        ordered_scores = PreMatchingScore.objects.filter(prematching=self.pre_matching).order_by("-score")

        self.assertEqual(ordered_scores[0].id, score2.id)  # 90
        self.assertEqual(ordered_scores[1].id, score3.id)  # 80
        self.assertEqual(ordered_scores[2].id, score1.id)  # 70

    def test_pre_matching_score_negative_score(self):
        """음수 점수를 설정할 수 있는지 테스트"""
        # IntegerField이므로 음수 가능
        score = PreMatchingScore.objects.create(
            prematching=self.pre_matching,
            algorithm_category="Algorithm1",
            score=-10,
        )

        self.assertEqual(score.score, -10)

    def test_pre_matching_score_zero_score(self):
        """0점을 설정할 수 있는지 테스트"""
        score = PreMatchingScore.objects.create(
            prematching=self.pre_matching,
            algorithm_category="Algorithm1",
            score=0,
        )

        self.assertEqual(score.score, 0)

    def test_pre_matching_score_high_score(self):
        """높은 점수를 설정할 수 있는지 테스트"""
        score = PreMatchingScore.objects.create(
            prematching=self.pre_matching,
            algorithm_category="Algorithm1",
            score=10000,
        )

        self.assertEqual(score.score, 10000)
