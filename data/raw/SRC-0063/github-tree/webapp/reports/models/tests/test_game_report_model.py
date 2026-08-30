from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

import pytest
from games.models import Game, GameResult, GameSession
from reports.models import GameReport, Report

from users.models import Child

User = get_user_model()


@pytest.mark.django_db
class GameReportModelTests(TestCase):
    """GameReport 모델 테스트"""

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
            code="TEST_GAME",
            max_round=10,
            is_active=True,
        )

    def test_create_game_report(self):
        """게임 레포트 생성 테스트"""
        game_report = GameReport.objects.create(
            report=self.report,
            game=self.game,
        )

        self.assertEqual(game_report.report, self.report)
        self.assertEqual(game_report.game, self.game)
        self.assertEqual(game_report.total_plays_count, 0)
        self.assertEqual(game_report.total_success_count, 0)
        self.assertEqual(game_report.total_wrong_count, 0)

    def test_unique_report_game_constraint(self):
        """레포트와 게임 조합의 유일성 제약 테스트"""
        GameReport.objects.create(
            report=self.report,
            game=self.game,
        )

        with self.assertRaises(IntegrityError):
            GameReport.objects.create(
                report=self.report,
                game=self.game,
            )

    def test_get_or_create_for_report_and_game_creates_new(self):
        """get_or_create_for_report_and_game 메서드 - 새로 생성"""
        game_report, created = GameReport.objects.get_or_create_for_report_and_game(
            report=self.report,
            game=self.game,
        )

        self.assertTrue(created)
        self.assertEqual(game_report.report, self.report)
        self.assertEqual(game_report.game, self.game)

    def test_get_or_create_for_report_and_game_gets_existing(self):
        """get_or_create_for_report_and_game 메서드 - 기존 조회"""
        existing_report = GameReport.objects.create(
            report=self.report,
            game=self.game,
            total_plays_count=5,
        )

        game_report, created = GameReport.objects.get_or_create_for_report_and_game(
            report=self.report,
            game=self.game,
        )

        self.assertFalse(created)
        self.assertEqual(game_report.id, existing_report.id)
        self.assertEqual(game_report.total_plays_count, 5)

    def test_get_total_reaction_ms_avg_with_actions(self):
        """평균 반응시간 계산 테스트 - 액션이 있는 경우"""
        game_report = GameReport.objects.create(
            report=self.report,
            game=self.game,
            total_reaction_ms_sum=5000,
            total_play_actions_count=10,
        )

        avg = game_report.get_total_reaction_ms_avg()
        self.assertEqual(avg, 500)

    def test_get_total_reaction_ms_avg_without_actions(self):
        """평균 반응시간 계산 테스트 - 액션이 없는 경우"""
        game_report = GameReport.objects.create(
            report=self.report,
            game=self.game,
            total_reaction_ms_sum=0,
            total_play_actions_count=0,
        )

        avg = game_report.get_total_reaction_ms_avg()
        self.assertIsNone(avg)

    def test_get_wrong_rate_with_actions(self):
        """오답률 계산 테스트 - 액션이 있는 경우"""
        game_report = GameReport.objects.create(
            report=self.report,
            game=self.game,
            total_success_count=70,
            total_wrong_count=30,
            total_play_actions_count=100,
        )

        wrong_rate = game_report.get_wrong_rate()
        self.assertEqual(wrong_rate, 30.0)

    def test_get_wrong_rate_without_actions(self):
        """오답률 계산 테스트 - 액션이 없는 경우"""
        game_report = GameReport.objects.create(
            report=self.report,
            game=self.game,
            total_play_actions_count=0,
        )

        wrong_rate = game_report.get_wrong_rate()
        self.assertIsNone(wrong_rate)

    def test_get_avg_rounds_count_with_plays(self):
        """평균 도달 라운드 계산 테스트 - 플레이가 있는 경우"""
        game_report = GameReport.objects.create(
            report=self.report,
            game=self.game,
            total_plays_count=5,
            total_play_rounds_count=25,
        )

        avg_rounds = game_report.get_avg_rounds_count()
        self.assertEqual(avg_rounds, 5.0)

    def test_get_avg_rounds_count_without_plays(self):
        """평균 도달 라운드 계산 테스트 - 플레이가 없는 경우"""
        game_report = GameReport.objects.create(
            report=self.report,
            game=self.game,
            total_plays_count=0,
        )

        avg_rounds = game_report.get_avg_rounds_count()
        self.assertIsNone(avg_rounds)

    def test_get_actual_latest_session_id(self):
        """최신 세션 ID 조회 테스트"""
        session = GameSession.objects.create(parent=self.user, game=self.game, child=self.child)
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

        latest_session_id = game_report.get_actual_latest_session_id()
        self.assertEqual(latest_session_id, session.id)

    def test_get_actual_latest_session_id_no_results(self):
        """최신 세션 ID 조회 테스트 - 결과가 없는 경우"""
        game_report = GameReport.objects.create(
            report=self.report,
            game=self.game,
        )

        latest_session_id = game_report.get_actual_latest_session_id()
        self.assertIsNone(latest_session_id)

    def test_is_up_to_date_when_synced(self):
        """최신 상태 확인 테스트 - 동기화된 경우"""
        session = GameSession.objects.create(parent=self.user, game=self.game, child=self.child)
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
            last_reflected_session=session,
        )

        self.assertTrue(game_report.is_up_to_date())

    def test_is_up_to_date_when_not_synced(self):
        """최신 상태 확인 테스트 - 동기화되지 않은 경우"""
        session1 = GameSession.objects.create(parent=self.user, game=self.game, child=self.child)
        session2 = GameSession.objects.create(parent=self.user, game=self.game, child=self.child)

        GameResult.objects.create(
            child=self.child,
            game=self.game,
            session=session1,
            round_count=5,
            success_count=10,
            wrong_count=2,
            score=100,
        )
        # 더 최신 결과
        GameResult.objects.create(
            child=self.child,
            game=self.game,
            session=session2,
            round_count=6,
            success_count=12,
            wrong_count=1,
            score=100,
        )

        game_report = GameReport.objects.create(
            report=self.report,
            game=self.game,
            last_reflected_session=session1,  # 이전 세션 참조
        )

        self.assertFalse(game_report.is_up_to_date())

    def test_aggregate_statistics_with_results(self):
        """통계 집계 테스트 - 결과가 있는 경우"""
        session1 = GameSession.objects.create(parent=self.user, game=self.game, child=self.child)
        session2 = GameSession.objects.create(parent=self.user, game=self.game, child=self.child)

        GameResult.objects.create(
            child=self.child,
            game=self.game,
            session=session1,
            round_count=10,
            success_count=20,
            wrong_count=5,
            score=100,
            reaction_ms_sum=3000,
        )
        GameResult.objects.create(
            child=self.child,
            game=self.game,
            session=session2,
            round_count=8,
            success_count=15,
            wrong_count=3,
            score=100,
            reaction_ms_sum=2500,
        )

        game_report = GameReport.objects.create(
            report=self.report,
            game=self.game,
        )

        result = game_report.aggregate_statistics()

        self.assertTrue(result)
        game_report.refresh_from_db()
        self.assertEqual(game_report.total_plays_count, 2)
        self.assertEqual(game_report.total_play_rounds_count, 18)
        self.assertEqual(game_report.total_success_count, 35)
        self.assertEqual(game_report.total_wrong_count, 8)
        self.assertEqual(game_report.total_play_actions_count, 43)
        self.assertEqual(game_report.total_reaction_ms_sum, 5500)
        self.assertEqual(game_report.max_rounds_count, 1)  # max_round=10인 결과 1개

    def test_aggregate_statistics_without_results(self):
        """통계 집계 테스트 - 결과가 없는 경우"""
        game_report = GameReport.objects.create(
            report=self.report,
            game=self.game,
        )

        result = game_report.aggregate_statistics()

        self.assertFalse(result)
        game_report.refresh_from_db()
        self.assertEqual(game_report.total_plays_count, 0)
        self.assertEqual(game_report.total_play_rounds_count, 0)
        self.assertEqual(game_report.total_success_count, 0)
        self.assertEqual(game_report.total_wrong_count, 0)

    def test_get_game_results(self):
        """게임 결과 조회 테스트"""
        session1 = GameSession.objects.create(parent=self.user, game=self.game, child=self.child)
        session2 = GameSession.objects.create(parent=self.user, game=self.game, child=self.child)

        result1 = GameResult.objects.create(
            child=self.child,
            game=self.game,
            session=session1,
            round_count=5,
            success_count=10,
            wrong_count=2,
            score=100,
        )
        result2 = GameResult.objects.create(
            child=self.child,
            game=self.game,
            session=session2,
            round_count=7,
            success_count=14,
            wrong_count=1,
            score=100,
        )

        game_report = GameReport.objects.create(
            report=self.report,
            game=self.game,
        )

        results = game_report.get_game_results()
        self.assertEqual(results.count(), 2)
        # created_at 역순으로 정렬
        self.assertEqual(results[0].id, result2.id)
        self.assertEqual(results[1].id, result1.id)

    def test_get_recent_trends(self):
        """최근 트렌드 조회 테스트"""
        for i in range(5):
            session = GameSession.objects.create(parent=self.user, game=self.game, child=self.child)
            GameResult.objects.create(
                child=self.child,
                game=self.game,
                session=session,
                round_count=i + 1,
                success_count=(i + 1) * 2,
                wrong_count=i,
                score=100,
                reaction_ms_sum=(i + 1) * 100,
            )

        game_report = GameReport.objects.create(
            report=self.report,
            game=self.game,
        )

        # 기본값 3개
        trends = game_report.get_recent_trends()
        self.assertEqual(len(trends), 3)

        # 최근 2개만
        trends_2 = game_report.get_recent_trends(limit=2)
        self.assertEqual(len(trends_2), 2)

    def test_by_report_manager_method(self):
        """by_report 매니저 메서드 테스트"""
        game2 = Game.objects.create(
            name="Game 2",
            code="GAME_2",
            max_round=5,
            is_active=True,
        )

        gr1 = GameReport.objects.create(report=self.report, game=self.game)
        gr2 = GameReport.objects.create(report=self.report, game=game2)

        user2 = User.objects.create_user(username="user2", password="pass")
        child2 = Child.objects.create(
            parent=user2,
            name="Child 2",
            birth_year=2020,
            gender="M",
        )
        report2 = Report.objects.create(user=user2, child=child2)
        GameReport.objects.create(report=report2, game=self.game)

        reports_for_report1 = GameReport.objects.by_report(self.report)
        self.assertEqual(reports_for_report1.count(), 2)
        self.assertIn(gr1, reports_for_report1)
        self.assertIn(gr2, reports_for_report1)

    def test_by_game_manager_method(self):
        """by_game 매니저 메서드 테스트"""
        user2 = User.objects.create_user(username="user2", password="pass")
        child2 = Child.objects.create(
            parent=user2,
            name="Child 2",
            birth_year=2020,
            gender="M",
        )
        report2 = Report.objects.create(user=user2, child=child2)

        gr1 = GameReport.objects.create(report=self.report, game=self.game)
        gr2 = GameReport.objects.create(report=report2, game=self.game)

        game2 = Game.objects.create(
            name="Game 2",
            code="GAME_2",
            max_round=5,
            is_active=True,
        )
        GameReport.objects.create(report=self.report, game=game2)

        reports_for_game = GameReport.objects.by_game(self.game)
        self.assertEqual(reports_for_game.count(), 2)
        self.assertIn(gr1, reports_for_game)
        self.assertIn(gr2, reports_for_game)

    def test_game_report_str_representation(self):
        """게임 레포트 문자열 표현 테스트"""
        game_report = GameReport.objects.create(
            report=self.report,
            game=self.game,
        )

        expected = f"{self.report} - {self.game.name}"
        self.assertEqual(str(game_report), expected)
