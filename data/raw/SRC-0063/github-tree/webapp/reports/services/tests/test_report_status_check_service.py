from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

import pytest
from games.models import Game, GameResult, GameSession
from reports.choices import ReportStatusChoice
from reports.models import GameReport, Report
from reports.services.report_status_check_service import ReportStatusCheckService

from users.models import Child

User = get_user_model()


@pytest.mark.django_db
class ReportStatusCheckServiceTests(TestCase):
    """ReportStatusCheckService 테스트"""

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
        self.game1 = Game.objects.create(
            name="Game 1",
            code="GAME_1",
            max_round=10,
            is_active=True,
        )
        self.game2 = Game.objects.create(
            name="Game 2",
            code="GAME_2",
            max_round=5,
            is_active=True,
        )
        # Alias for backward compatibility with test fixtures
        self.game = self.game1

    def test_initialization(self):
        """서비스 초기화 테스트"""
        service = ReportStatusCheckService(self.report)

        self.assertEqual(service.report, self.report)
        self.assertEqual(service.child, self.child)

    def test_check_status_no_games_played(self):
        """게임을 플레이하지 않았을 때 상태 체크 테스트"""
        service = ReportStatusCheckService(self.report)
        service.check_status()

        self.report.refresh_from_db()
        self.assertEqual(self.report.status, ReportStatusChoice.NO_GAMES_PLAYED)

    @patch("reports.services.report_status_check_service.generate_report_task.delay")
    def test_check_status_triggers_generation(self, mock_task):
        """게임 플레이가 있고 동기화가 필요할 때 생성 트리거 테스트"""
        # 각 게임에 대해 별도의 세션 생성
        session1 = GameSession.objects.create(parent=self.user, game=self.game1, child=self.child)
        session2 = GameSession.objects.create(parent=self.user, game=self.game2, child=self.child)

        # 게임 결과 생성
        GameResult.objects.create(
            child=self.child,
            game=self.game1,
            session=session1,
            round_count=5,
            success_count=10,
            wrong_count=2,
            score=100,
        )
        GameResult.objects.create(
            child=self.child,
            game=self.game2,
            session=session2,
            round_count=3,
            success_count=6,
            wrong_count=1,
            score=100,
        )

        service = ReportStatusCheckService(self.report)
        service.check_status()

        self.report.refresh_from_db()
        self.assertEqual(self.report.status, ReportStatusChoice.GENERATING)

        # Celery task가 호출되었는지 확인
        mock_task.assert_called_once_with(
            user_id=self.user.id,
            child_id=self.child.id,
        )

    def test_check_status_all_up_to_date(self):
        """모든 게임이 최신 상태일 때 테스트"""
        # 각 게임에 대해 별도의 세션 생성 (GameResult는 session당 하나만 가능)
        session1 = GameSession.objects.create(parent=self.user, game=self.game1, child=self.child)
        session2 = GameSession.objects.create(parent=self.user, game=self.game2, child=self.child)

        # 모든 게임에 대한 게임 결과 생성
        GameResult.objects.create(
            child=self.child,
            game=self.game1,
            session=session1,
            round_count=5,
            success_count=10,
            wrong_count=2,
            score=100,
        )
        GameResult.objects.create(
            child=self.child,
            game=self.game2,
            session=session2,
            round_count=3,
            success_count=6,
            wrong_count=1,
            score=100,
        )

        # 게임 레포트 생성 (최신 세션으로 설정)
        GameReport.objects.create(
            report=self.report,
            game=self.game1,
            last_reflected_session=session1,
        )
        GameReport.objects.create(
            report=self.report,
            game=self.game2,
            last_reflected_session=session2,
        )

        service = ReportStatusCheckService(self.report)
        service.check_status()

        self.report.refresh_from_db()
        self.assertEqual(self.report.status, ReportStatusChoice.COMPLETED)

    def test_check_status_skips_when_generating(self):
        """이미 GENERATING 상태일 때 건너뛰기 테스트"""
        self.report.status = ReportStatusChoice.GENERATING
        self.report.save()

        # 게임 결과 생성
        session = GameSession.objects.create(parent=self.user, game=self.game, child=self.child)
        GameResult.objects.create(
            child=self.child,
            game=self.game1,
            session=session,
            round_count=5,
            success_count=10,
            wrong_count=2,
            score=100,
        )

        with patch("reports.services.report_status_check_service.generate_report_task.delay") as mock_task:
            service = ReportStatusCheckService(self.report)
            service.check_status()

            # 상태가 그대로 유지
            self.report.refresh_from_db()
            self.assertEqual(self.report.status, ReportStatusChoice.GENERATING)

            # task가 호출되지 않음
            mock_task.assert_not_called()

    @patch("reports.services.report_status_check_service.generate_report_task.delay")
    def test_check_status_error_handling(self, mock_task):
        """레포트 생성 트리거 중 오류 발생 시 처리 테스트"""
        # 각 게임에 대해 별도의 세션 생성
        session1 = GameSession.objects.create(parent=self.user, game=self.game1, child=self.child)
        session2 = GameSession.objects.create(parent=self.user, game=self.game2, child=self.child)

        # 모든 게임에 대한 게임 결과 생성
        GameResult.objects.create(
            child=self.child,
            game=self.game1,
            session=session1,
            round_count=5,
            success_count=10,
            wrong_count=2,
            score=100,
        )
        GameResult.objects.create(
            child=self.child,
            game=self.game2,
            session=session2,
            round_count=3,
            success_count=6,
            wrong_count=1,
            score=100,
        )

        # task 호출 시 예외 발생
        mock_task.side_effect = Exception("Celery error")

        service = ReportStatusCheckService(self.report)
        service.check_status()

        # 오류 발생 시 ERROR 상태로 변경
        self.report.refresh_from_db()
        self.assertEqual(self.report.status, ReportStatusChoice.ERROR)

    def test_is_all_played(self):
        """모든 게임 플레이 여부 확인 테스트"""
        session1 = GameSession.objects.create(parent=self.user, game=self.game1, child=self.child)

        # 게임 1만 플레이
        GameResult.objects.create(
            child=self.child,
            game=self.game1,
            session=session1,
            round_count=5,
            success_count=10,
            wrong_count=2,
            score=100,
        )

        service = ReportStatusCheckService(self.report)

        # 아직 게임 2를 플레이하지 않음
        self.assertFalse(service._is_all_played())

        # 게임 2도 플레이 (별도의 세션 생성)
        session2 = GameSession.objects.create(parent=self.user, game=self.game2, child=self.child)
        GameResult.objects.create(
            child=self.child,
            game=self.game2,
            session=session2,
            round_count=3,
            success_count=6,
            wrong_count=1,
            score=100,
        )

        # 새 서비스 인스턴스 생성 (상태 갱신)
        service = ReportStatusCheckService(self.report)
        self.assertTrue(service._is_all_played())

    def test_is_all_up_to_date(self):
        """모든 게임이 최신 상태인지 확인 테스트"""
        # 각 게임에 대해 별도의 세션 생성
        session1 = GameSession.objects.create(parent=self.user, game=self.game1, child=self.child)
        session2 = GameSession.objects.create(parent=self.user, game=self.game2, child=self.child)

        # 모든 게임에 대한 게임 결과 생성
        GameResult.objects.create(
            child=self.child,
            game=self.game1,
            session=session1,
            round_count=5,
            success_count=10,
            wrong_count=2,
            score=100,
        )
        GameResult.objects.create(
            child=self.child,
            game=self.game2,
            session=session2,
            round_count=3,
            success_count=6,
            wrong_count=1,
            score=100,
        )

        # 게임 1 레포트만 생성 (최신 상태)
        GameReport.objects.create(
            report=self.report,
            game=self.game1,
            last_reflected_session=session1,
        )

        service = ReportStatusCheckService(self.report)

        # 게임 2 레포트가 없으므로 최신 상태 아님
        self.assertFalse(service._is_all_up_to_date())

        # 게임 2 레포트도 생성
        GameReport.objects.create(
            report=self.report,
            game=self.game2,
            last_reflected_session=session2,
        )

        # 새 서비스 인스턴스 생성 (상태 갱신)
        service = ReportStatusCheckService(self.report)
        self.assertTrue(service._is_all_up_to_date())

    def test_played_game_ids(self):
        """플레이한 게임 ID 목록 조회 테스트"""
        session = GameSession.objects.create(parent=self.user, game=self.game, child=self.child)

        # 게임 1만 플레이
        GameResult.objects.create(
            child=self.child,
            game=self.game1,
            session=session,
            round_count=5,
            success_count=10,
            wrong_count=2,
            score=100,
        )

        service = ReportStatusCheckService(self.report)

        played_ids = service.played_game_ids
        self.assertEqual(len(played_ids), 1)
        self.assertIn(self.game1.id, played_ids)
        self.assertNotIn(self.game2.id, played_ids)

    def test_unplayed_game_ids(self):
        """플레이하지 않은 게임 ID 목록 조회 테스트"""
        session = GameSession.objects.create(parent=self.user, game=self.game, child=self.child)

        # 게임 1만 플레이
        GameResult.objects.create(
            child=self.child,
            game=self.game1,
            session=session,
            round_count=5,
            success_count=10,
            wrong_count=2,
            score=100,
        )

        service = ReportStatusCheckService(self.report)

        unplayed_ids = service.unplayed_game_ids
        self.assertEqual(len(unplayed_ids), 1)
        self.assertNotIn(self.game1.id, unplayed_ids)
        self.assertIn(self.game2.id, unplayed_ids)

    def test_outdated_result_game_ids(self):
        """최신 세션이 반영되지 않은 게임 ID 목록 조회 테스트"""
        session1 = GameSession.objects.create(parent=self.user, game=self.game, child=self.child)
        session2 = GameSession.objects.create(parent=self.user, game=self.game, child=self.child)

        # 게임 1 결과
        GameResult.objects.create(
            child=self.child,
            game=self.game1,
            session=session1,
            round_count=5,
            success_count=10,
            wrong_count=2,
            score=100,
        )

        # 더 최신 결과
        GameResult.objects.create(
            child=self.child,
            game=self.game1,
            session=session2,
            round_count=7,
            success_count=14,
            wrong_count=1,
            score=100,
        )

        # 게임 레포트 생성 (이전 세션 참조)
        GameReport.objects.create(
            report=self.report,
            game=self.game1,
            last_reflected_session=session1,
        )

        service = ReportStatusCheckService(self.report)

        outdated_ids = service.outdated_result_game_ids
        self.assertIn(self.game1.id, outdated_ids)

    def test_with_inactive_games(self):
        """비활성화된 게임은 고려하지 않는 테스트"""
        # 게임 2 비활성화
        self.game2.is_active = False
        self.game2.save()

        session = GameSession.objects.create(parent=self.user, game=self.game, child=self.child)

        # 게임 1만 플레이
        GameResult.objects.create(
            child=self.child,
            game=self.game1,
            session=session,
            round_count=5,
            success_count=10,
            wrong_count=2,
            score=100,
        )

        GameReport.objects.create(
            report=self.report,
            game=self.game1,
            last_reflected_session=session,
        )

        service = ReportStatusCheckService(self.report)

        # 게임 2는 비활성화되어 있으므로 모두 플레이한 것으로 간주
        self.assertTrue(service._is_all_played())
        self.assertTrue(service._is_all_up_to_date())
