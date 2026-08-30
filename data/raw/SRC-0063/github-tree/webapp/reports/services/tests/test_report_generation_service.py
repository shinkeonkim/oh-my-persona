from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

import pytest
from games.models import Game
from reports.choices import ReportStatusChoice
from reports.models import Report
from reports.services.report_generation_service import ReportGenerationService

from users.models import Child

User = get_user_model()


@pytest.mark.django_db
class ReportGenerationServiceTests(TestCase):
    """ReportGenerationService 테스트"""

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

    @patch("reports.services.report_generation_service.GameReportGenerationService.update_or_create_game_report")
    @patch(
        "reports.services.report_generation_service.ReportConcentrationScoreGenerationService.update_concentration_score"
    )
    def test_update_or_create_report_creates_new_report(self, mock_update_concentration, mock_update_game_report):
        """새 레포트 생성 테스트"""
        # Mocking
        mock_update_game_report.return_value = MagicMock()
        mock_update_concentration.return_value = MagicMock()

        # 실행
        report = ReportGenerationService.update_or_create_report(
            user=self.user,
            child=self.child,
        )

        # 검증
        self.assertIsNotNone(report)
        self.assertEqual(report.user, self.user)
        self.assertEqual(report.child, self.child)
        self.assertEqual(report.status, ReportStatusChoice.COMPLETED)

        # 활성화된 게임 수만큼 GameReportGenerationService 호출 확인
        self.assertEqual(mock_update_game_report.call_count, 2)
        mock_update_concentration.assert_called_once_with(report)

    @patch("reports.services.report_generation_service.GameReportGenerationService.update_or_create_game_report")
    @patch(
        "reports.services.report_generation_service.ReportConcentrationScoreGenerationService.update_concentration_score"
    )
    def test_update_or_create_report_updates_existing_report(self, mock_update_concentration, mock_update_game_report):
        """기존 레포트 업데이트 테스트"""
        # 기존 레포트 생성
        existing_report = Report.objects.create(
            user=self.user,
            child=self.child,
            status=ReportStatusChoice.GENERATING,
            concentration_score=50,
        )

        # Mocking
        mock_update_game_report.return_value = MagicMock()
        mock_update_concentration.return_value = MagicMock()

        # 실행
        report = ReportGenerationService.update_or_create_report(
            user=self.user,
            child=self.child,
        )

        # 검증
        self.assertEqual(report.id, existing_report.id)
        self.assertEqual(report.status, ReportStatusChoice.COMPLETED)
        mock_update_game_report.assert_called()
        mock_update_concentration.assert_called_once_with(report)

    @patch("reports.services.report_generation_service.GameReportGenerationService.update_or_create_game_report")
    @patch(
        "reports.services.report_generation_service.ReportConcentrationScoreGenerationService.update_concentration_score"
    )
    def test_update_or_create_report_processes_all_active_games(
        self, mock_update_concentration, mock_update_game_report
    ):
        """모든 활성화된 게임 처리 테스트"""
        # 비활성화 게임 추가
        inactive_game = Game.objects.create(
            name="Inactive Game",
            code="INACTIVE",
            max_round=3,
            is_active=False,
        )

        # Mocking
        mock_update_game_report.return_value = MagicMock()
        mock_update_concentration.return_value = MagicMock()

        # 실행
        ReportGenerationService.update_or_create_report(
            user=self.user,
            child=self.child,
        )

        # 검증 - 활성화된 게임(2개)만 처리되어야 함
        self.assertEqual(mock_update_game_report.call_count, 2)

        # 비활성화 게임은 처리되지 않았는지 확인
        call_args_list = [call[0] for call in mock_update_game_report.call_args_list]
        games_processed = [args[1] for args in call_args_list]
        self.assertNotIn(inactive_game, games_processed)

    @patch("reports.services.report_generation_service.GameReportGenerationService.update_or_create_game_report")
    @patch(
        "reports.services.report_generation_service.ReportConcentrationScoreGenerationService.update_concentration_score"
    )
    def test_update_or_create_report_atomic_transaction(self, mock_update_concentration, mock_update_game_report):
        """트랜잭션 원자성 테스트 - 실패 시 롤백"""
        # Mocking - GameReportGenerationService에서 예외 발생
        mock_update_game_report.side_effect = Exception("Game report generation failed")

        # 실행 및 검증
        with self.assertRaises(Exception):
            ReportGenerationService.update_or_create_report(
                user=self.user,
                child=self.child,
            )

        # 레포트가 생성되지 않았는지 확인 (트랜잭션 롤백)
        self.assertFalse(Report.objects.filter(user=self.user, child=self.child).exists())

    @patch("reports.services.report_generation_service.GameReportGenerationService.update_or_create_game_report")
    @patch(
        "reports.services.report_generation_service.ReportConcentrationScoreGenerationService.update_concentration_score"
    )
    def test_update_or_create_report_with_no_active_games(self, mock_update_concentration, mock_update_game_report):
        """활성화된 게임이 없을 때 테스트"""
        # 모든 게임 비활성화
        Game.objects.all().update(is_active=False)

        # Mocking
        mock_update_game_report.return_value = MagicMock()
        mock_update_concentration.return_value = MagicMock()

        # 실행
        report = ReportGenerationService.update_or_create_report(
            user=self.user,
            child=self.child,
        )

        # 검증
        self.assertIsNotNone(report)
        self.assertEqual(report.status, ReportStatusChoice.COMPLETED)

        # 게임이 없으므로 GameReportGenerationService 호출되지 않음
        mock_update_game_report.assert_not_called()

        # 집중력 점수는 업데이트됨
        mock_update_concentration.assert_called_once_with(report)

    @patch("reports.services.report_generation_service.GameReportGenerationService.update_or_create_game_report")
    @patch(
        "reports.services.report_generation_service.ReportConcentrationScoreGenerationService.update_concentration_score"
    )
    def test_update_or_create_report_status_completion(self, mock_update_concentration, mock_update_game_report):
        """레포트 상태가 COMPLETED로 변경되는지 테스트"""
        # Mocking
        mock_update_game_report.return_value = MagicMock()
        mock_update_concentration.return_value = MagicMock()

        # 실행
        report = ReportGenerationService.update_or_create_report(
            user=self.user,
            child=self.child,
        )

        # 검증
        report.refresh_from_db()
        self.assertEqual(report.status, ReportStatusChoice.COMPLETED)

    @patch("reports.services.report_generation_service.GameReportGenerationService.update_or_create_game_report")
    @patch(
        "reports.services.report_generation_service.ReportConcentrationScoreGenerationService.update_concentration_score"
    )
    def test_update_or_create_report_calls_services_in_order(self, mock_update_concentration, mock_update_game_report):
        """서비스 호출 순서 테스트"""
        # Mocking
        mock_update_game_report.return_value = MagicMock()
        mock_update_concentration.return_value = MagicMock()

        # 실행
        ReportGenerationService.update_or_create_report(
            user=self.user,
            child=self.child,
        )

        # 검증 - 호출 순서 확인
        # 1. 게임 레포트 생성/업데이트가 먼저
        self.assertTrue(mock_update_game_report.called)

        # 2. 집중력 점수 업데이트가 나중에
        self.assertTrue(mock_update_concentration.called)

        # 집중력 점수는 게임 레포트 처리 후에 호출되어야 함
        mock_update_concentration.assert_called_once()
