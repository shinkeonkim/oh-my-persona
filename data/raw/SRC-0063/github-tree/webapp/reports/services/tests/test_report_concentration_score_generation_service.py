from django.contrib.auth import get_user_model
from django.test import TestCase

import pytest
from games.choices import GameCodeChoice
from games.models import Game, GameResult, GameSession
from reports.models import GameReport, Report
from reports.services.report_concentration_score_generation_service import (
    ReportConcentrationScoreGenerationService,
)

from users.models import Child

User = get_user_model()


@pytest.mark.django_db
class ReportConcentrationScoreGenerationServiceTests(TestCase):
    """ReportConcentrationScoreGenerationService 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
        )
        self.child = Child.objects.create(
            parent=self.user,
            name="Test Child",
            birth_year=2020,
            gender="M",
        )
        self.report = Report.objects.create(
            user=self.user,
            child=self.child,
        )
        self.game = Game.objects.create(
            name="Test Game",
            code=GameCodeChoice.KIDS_TRAFFIC,
            max_round=10,
            is_active=True,
        )

    def test_calculate_concentration_score_with_no_game_reports(self):
        """게임 레포트가 없을 때 집중력 점수 계산 테스트"""
        score = ReportConcentrationScoreGenerationService.calculate_concentration_score(self.report)

        self.assertEqual(score, 0)

    def test_calculate_concentration_score_with_no_plays(self):
        """플레이가 없을 때 집중력 점수 계산 테스트"""
        # 플레이가 없는 게임 레포트
        GameReport.objects.create(
            report=self.report,
            game=self.game,
            total_plays_count=0,
        )

        score = ReportConcentrationScoreGenerationService.calculate_concentration_score(self.report)

        self.assertEqual(score, 0)

    def test_calculate_concentration_score_perfect_performance(self):
        """완벽한 성능일 때 집중력 점수 계산 테스트"""
        session = GameSession.objects.create(parent=self.user, game=self.game, child=self.child)

        # 완벽한 결과
        GameResult.objects.create(
            child=self.child,
            game=self.game,
            session=session,
            round_count=10,  # max_round
            success_count=50,
            wrong_count=0,
            score=100,
        )

        game_report = GameReport.objects.create(
            report=self.report,
            game=self.game,
        )
        game_report.aggregate_statistics()

        score = ReportConcentrationScoreGenerationService.calculate_concentration_score(self.report)

        # 완벽한 성능이므로 100점에 가까워야 함
        self.assertGreaterEqual(score, 90)
        self.assertLessEqual(score, 100)

    def test_calculate_concentration_score_poor_performance(self):
        """낮은 성능일 때 집중력 점수 계산 테스트"""
        session = GameSession.objects.create(parent=self.user, game=self.game, child=self.child)

        # 낮은 성능
        GameResult.objects.create(
            child=self.child,
            game=self.game,
            session=session,
            round_count=2,  # 매우 낮은 라운드
            success_count=5,
            wrong_count=15,  # 높은 오답률
            score=50,
        )

        game_report = GameReport.objects.create(
            report=self.report,
            game=self.game,
        )
        game_report.aggregate_statistics()

        score = ReportConcentrationScoreGenerationService.calculate_concentration_score(self.report)

        # 낮은 성능이므로 점수가 낮아야 함
        self.assertLess(score, 50)

    def test_calculate_success_rate_score(self):
        """성공률 점수 계산 테스트"""
        game_report = GameReport.objects.create(
            report=self.report,
            game=self.game,
            total_success_count=80,
            total_wrong_count=20,
            total_play_actions_count=100,
        )

        score = ReportConcentrationScoreGenerationService._calculate_success_rate_score(game_report)

        # 80% 성공률
        self.assertEqual(score, 80.0)

    def test_calculate_success_rate_score_no_actions(self):
        """액션이 없을 때 성공률 점수 계산 테스트"""
        game_report = GameReport.objects.create(
            report=self.report,
            game=self.game,
            total_play_actions_count=0,
        )

        score = ReportConcentrationScoreGenerationService._calculate_success_rate_score(game_report)

        self.assertEqual(score, 0.0)

    def test_calculate_max_round_score(self):
        """최대 라운드 점수 계산 테스트"""
        game_report = GameReport.objects.create(
            report=self.report,
            game=self.game,
            total_plays_count=10,
            max_rounds_count=5,  # 50% max round 도달
            total_play_rounds_count=80,  # 평균 8 라운드
        )

        score = ReportConcentrationScoreGenerationService._calculate_max_round_score(game_report)

        # (50% * 0.6) + (80% * 0.4) = 30 + 32 = 62
        self.assertGreater(score, 50)
        self.assertLess(score, 70)

    def test_calculate_consistency_score(self):
        """일관성 점수 계산 테스트"""
        game_report = GameReport.objects.create(
            report=self.report,
            game=self.game,
            total_success_count=70,
            total_wrong_count=30,
            total_play_actions_count=100,
        )

        score = ReportConcentrationScoreGenerationService._calculate_consistency_score(game_report)

        # 오답률 30% -> 일관성 점수 70
        self.assertEqual(score, 70.0)

    def test_calculate_consistency_score_perfect(self):
        """완벽한 일관성 점수 계산 테스트"""
        game_report = GameReport.objects.create(
            report=self.report,
            game=self.game,
            total_success_count=100,
            total_wrong_count=0,
            total_play_actions_count=100,
        )

        score = ReportConcentrationScoreGenerationService._calculate_consistency_score(game_report)

        # 오답률 0% -> 일관성 점수 100
        self.assertEqual(score, 100.0)

    def test_calculate_improvement_score_with_improvement(self):
        """개선도 점수 계산 테스트 - 개선된 경우"""
        # 오래된 결과 (낮은 성공률)
        for i in range(3):
            session = GameSession.objects.create(parent=self.user, game=self.game, child=self.child)
            GameResult.objects.create(
                child=self.child,
                game=self.game,
                session=session,
                round_count=5,
                success_count=10,
                wrong_count=10,  # 50% 성공률
                score=50,
            )

        # 최근 결과 (높은 성공률)
        for i in range(2):
            session = GameSession.objects.create(parent=self.user, game=self.game, child=self.child)
            GameResult.objects.create(
                child=self.child,
                game=self.game,
                session=session,
                round_count=8,
                success_count=18,
                wrong_count=2,  # 90% 성공률
                score=90,
            )

        game_report = GameReport.objects.create(
            report=self.report,
            game=self.game,
        )

        score = ReportConcentrationScoreGenerationService._calculate_improvement_score(game_report)

        # 개선되었으므로 50점 이상
        self.assertGreater(score, 50)

    def test_calculate_improvement_score_with_few_results(self):
        """개선도 점수 계산 테스트 - 결과가 적을 때"""
        session = GameSession.objects.create(parent=self.user, game=self.game, child=self.child)

        # 결과 1개만
        GameResult.objects.create(
            child=self.child,
            game=self.game,
            session=session,
            round_count=5,
            success_count=10,
            wrong_count=2,
            score=100,
        )

        game_report = GameReport.objects.create(
            report=self.report,
            game=self.game,
        )

        score = ReportConcentrationScoreGenerationService._calculate_improvement_score(game_report)

        # 비교할 데이터가 부족하므로 기본 점수 50
        self.assertEqual(score, 50.0)

    def test_update_concentration_score(self):
        """집중력 점수 업데이트 테스트"""
        session = GameSession.objects.create(parent=self.user, game=self.game, child=self.child)

        GameResult.objects.create(
            child=self.child,
            game=self.game,
            session=session,
            round_count=8,
            success_count=40,
            wrong_count=10,
            score=100,
        )

        game_report = GameReport.objects.create(
            report=self.report,
            game=self.game,
        )
        game_report.aggregate_statistics()

        # 초기 점수 0
        self.assertEqual(self.report.concentration_score, 0)

        # 업데이트
        updated_report = ReportConcentrationScoreGenerationService.update_concentration_score(self.report)

        # 점수가 업데이트되었는지 확인
        self.assertGreater(updated_report.concentration_score, 0)
        self.assertLessEqual(updated_report.concentration_score, 100)

        # DB에서 다시 조회하여 확인
        updated_report.refresh_from_db()
        self.assertGreater(updated_report.concentration_score, 0)

    def test_concentration_score_multiple_games(self):
        """여러 게임의 집중력 점수 평균 계산 테스트"""
        game2 = Game.objects.create(
            name="Game 2",
            code=GameCodeChoice.BB_STAR,
            max_round=10,
            is_active=True,
        )

        session1 = GameSession.objects.create(parent=self.user, game=self.game, child=self.child)

        # 게임 1 - 좋은 성능
        GameResult.objects.create(
            child=self.child,
            game=self.game,
            session=session1,
            round_count=9,
            success_count=45,
            wrong_count=5,
            score=100,
        )

        game_report1 = GameReport.objects.create(
            report=self.report,
            game=self.game,
        )
        game_report1.aggregate_statistics()

        session2 = GameSession.objects.create(parent=self.user, game=game2, child=self.child)

        # 게임 2 - 보통 성능
        GameResult.objects.create(
            child=self.child,
            game=game2,
            session=session2,
            round_count=5,
            success_count=25,
            wrong_count=25,
            score=100,
        )

        game_report2 = GameReport.objects.create(
            report=self.report,
            game=game2,
        )
        game_report2.aggregate_statistics()

        # 점수 계산
        score = ReportConcentrationScoreGenerationService.calculate_concentration_score(self.report)

        # 두 게임의 평균 점수
        self.assertGreater(score, 0)
        self.assertLess(score, 100)

    def test_concentration_score_boundaries(self):
        """집중력 점수 경계값 테스트 (0-100)"""
        # 극단적으로 좋은 성능 (보너스 점수 포함해도 100 초과하지 않음)
        for i in range(10):
            session = GameSession.objects.create(parent=self.user, game=self.game, child=self.child)
            GameResult.objects.create(
                child=self.child,
                game=self.game,
                session=session,
                round_count=10,  # max_round
                success_count=50,
                wrong_count=0,
                score=100,
            )

        game_report = GameReport.objects.create(
            report=self.report,
            game=self.game,
        )
        game_report.aggregate_statistics()

        score = ReportConcentrationScoreGenerationService.calculate_concentration_score(self.report)

        # 100점 초과하지 않아야 함
        self.assertLessEqual(score, 100)
        self.assertGreaterEqual(score, 0)
