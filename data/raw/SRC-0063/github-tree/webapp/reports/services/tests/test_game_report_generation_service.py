from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

import pytest
from games.choices import GameCodeChoice
from games.models import Game, GameResult, GameSession
from reports.models import GameReport, GameReportAdvice, Report
from reports.services.game_report_generation_service import GameReportGenerationService

from users.models import Child

User = get_user_model()


@pytest.mark.django_db
class GameReportGenerationServiceTests(TestCase):
    """GameReportGenerationService 테스트"""

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
            name="Kids Traffic",
            code=GameCodeChoice.KIDS_TRAFFIC,
            max_round=10,
            is_active=True,
        )
        self.session = GameSession.objects.create(parent=self.user, game=self.game, child=self.child)

    def test_update_or_create_game_report_creates_new(self):
        """새 게임 레포트 생성 테스트"""
        # 게임 결과 생성
        GameResult.objects.create(
            child=self.child,
            game=self.game,
            session=self.session,
            round_count=5,
            success_count=10,
            wrong_count=2,
            score=100,
            reaction_ms_sum=3000,
        )

        with patch.object(GameReportGenerationService, "_generate_game_report_advice") as mock_generate_advice:
            # 실행
            game_report = GameReportGenerationService.update_or_create_game_report(
                report=self.report,
                game=self.game,
            )

            # 검증
            self.assertIsNotNone(game_report)
            self.assertEqual(game_report.report, self.report)
            self.assertEqual(game_report.game, self.game)
            self.assertEqual(game_report.total_plays_count, 1)
            self.assertEqual(game_report.total_success_count, 10)
            self.assertEqual(game_report.total_wrong_count, 2)

            # LLM 조언 생성 메서드 호출 확인
            mock_generate_advice.assert_called_once()

    def test_update_game_report_statistics_with_results(self):
        """게임 결과가 있을 때 통계 업데이트 테스트"""
        # 게임 결과 생성
        GameResult.objects.create(
            child=self.child,
            game=self.game,
            session=self.session,
            round_count=10,
            success_count=20,
            wrong_count=5,
            score=100,
            reaction_ms_sum=3000,
        )

        # 실행
        game_report = GameReportGenerationService._update_game_report_statistics(
            report=self.report,
            game=self.game,
        )

        # 검증
        self.assertIsNotNone(game_report)
        self.assertEqual(game_report.total_plays_count, 1)
        self.assertEqual(game_report.total_play_rounds_count, 10)
        self.assertEqual(game_report.total_success_count, 20)
        self.assertEqual(game_report.total_wrong_count, 5)
        self.assertEqual(game_report.total_reaction_ms_sum, 3000)
        self.assertEqual(game_report.total_play_actions_count, 25)
        self.assertEqual(game_report.max_rounds_count, 1)  # max_round=10

    def test_update_game_report_statistics_without_results(self):
        """게임 결과가 없을 때 통계 업데이트 테스트"""
        # 실행
        game_report = GameReportGenerationService._update_game_report_statistics(
            report=self.report,
            game=self.game,
        )

        # 검증 - 결과가 없으면 기존 레포트 반환
        self.assertIsNotNone(game_report)

    def test_update_game_report_statistics_skips_when_up_to_date(self):
        """이미 최신 상태일 때 통계 업데이트 건너뛰기 테스트"""
        # 게임 결과 생성
        GameResult.objects.create(
            child=self.child,
            game=self.game,
            session=self.session,
            round_count=5,
            success_count=10,
            wrong_count=2,
            score=100,
        )

        # 게임 레포트 생성 및 최신 세션으로 설정
        game_report = GameReport.objects.create(
            report=self.report,
            game=self.game,
            last_reflected_session=self.session,
        )

        # 실행
        result = GameReportGenerationService._update_game_report_statistics(
            report=self.report,
            game=self.game,
        )

        # 검증 - 업데이트 건너뛰고 기존 레포트 반환
        self.assertEqual(result.id, game_report.id)

    @patch("reports.services.game_report_generation_service.KidsTrafficGameReportAdviceGenerator")
    def test_generate_game_report_advice_kids_traffic(self, mock_generator_class):
        """Kids Traffic 게임 조언 생성 테스트 (LLM 모킹)"""
        # Mock LLM generator
        mock_generator = Mock()
        mock_generator.generate_advice.return_value = [
            {
                "title": "집중력 향상 필요",
                "description": "아이의 집중력이 평균보다 낮습니다.",
            },
            {
                "title": "반응 속도 개선",
                "description": "반응 속도를 개선하면 좋습니다.",
            },
        ]
        mock_generator_class.return_value = mock_generator

        # 게임 레포트 생성
        game_report = GameReport.objects.create(
            report=self.report,
            game=self.game,
            total_plays_count=5,
            total_success_count=20,
            total_wrong_count=5,
        )

        # 실행
        GameReportGenerationService._generate_game_report_advice(
            game_report=game_report,
            game=self.game,
        )

        # 검증
        advices = GameReportAdvice.objects.filter(game_report=game_report)
        self.assertEqual(advices.count(), 2)
        self.assertEqual(advices[1].title, "집중력 향상 필요")  # ordering by -created_at
        self.assertEqual(advices[0].title, "반응 속도 개선")

        # LLM 호출 확인
        mock_generator.generate_advice.assert_called_once()

    @patch("reports.services.game_report_generation_service.BBStarGameReportAdviceGenerator")
    def test_generate_game_report_advice_bb_star(self, mock_generator_class):
        """BB Star 게임 조언 생성 테스트 (LLM 모킹)"""
        # BB Star 게임 생성
        bb_game = Game.objects.create(
            name="BB Star",
            code=GameCodeChoice.BB_STAR,
            max_round=10,
            is_active=True,
        )

        # Mock LLM generator
        mock_generator = Mock()
        mock_generator.generate_advice.return_value = [
            {
                "title": "패턴 인식 훈련",
                "description": "패턴 인식 능력을 향상시키세요.",
            },
        ]
        mock_generator_class.return_value = mock_generator

        # 게임 레포트 생성
        game_report = GameReport.objects.create(
            report=self.report,
            game=bb_game,
            total_plays_count=3,
            total_success_count=15,
            total_wrong_count=3,
        )

        # 실행
        GameReportGenerationService._generate_game_report_advice(
            game_report=game_report,
            game=bb_game,
        )

        # 검증
        advices = GameReportAdvice.objects.filter(game_report=game_report)
        self.assertEqual(advices.count(), 1)
        self.assertEqual(advices[0].title, "패턴 인식 훈련")

        # LLM 호출 확인
        mock_generator.generate_advice.assert_called_once()

    def test_generate_game_report_advice_skips_when_no_data(self):
        """데이터가 없을 때 조언 생성 건너뛰기 테스트"""
        # 게임 레포트 생성 (플레이 횟수 0)
        game_report = GameReport.objects.create(
            report=self.report,
            game=self.game,
            total_plays_count=0,
        )

        # 실행
        GameReportGenerationService._generate_game_report_advice(
            game_report=game_report,
            game=self.game,
        )

        # 검증 - 조언이 생성되지 않음
        advices = GameReportAdvice.objects.filter(game_report=game_report)
        self.assertEqual(advices.count(), 0)

    @patch("reports.services.game_report_generation_service.KidsTrafficGameReportAdviceGenerator")
    def test_generate_game_report_advice_handles_llm_error(self, mock_generator_class):
        """LLM 오류 발생 시 처리 테스트"""
        # Mock LLM generator - 예외 발생
        mock_generator = Mock()
        mock_generator.generate_advice.side_effect = Exception("LLM API timeout")
        mock_generator_class.return_value = mock_generator

        # 게임 레포트 생성
        game_report = GameReport.objects.create(
            report=self.report,
            game=self.game,
            total_plays_count=5,
            total_success_count=20,
            total_wrong_count=5,
        )

        # 실행
        GameReportGenerationService._generate_game_report_advice(
            game_report=game_report,
            game=self.game,
        )

        # 검증 - 오류 메시지가 포함된 조언 생성
        advices = GameReportAdvice.objects.filter(game_report=game_report)
        self.assertEqual(advices.count(), 1)
        self.assertEqual(advices[0].title, "조언 생성 실패")
        self.assertIn("오류", advices[0].description)
        self.assertIsNotNone(advices[0].error_message)

    def test_generate_game_report_advice_unknown_game(self):
        """알 수 없는 게임 코드일 때 테스트"""
        # 알 수 없는 게임 코드
        unknown_game = Game.objects.create(
            name="Unknown Game",
            code="UNKNOWN_CODE",
            max_round=5,
            is_active=True,
        )

        # 게임 레포트 생성
        game_report = GameReport.objects.create(
            report=self.report,
            game=unknown_game,
            total_plays_count=5,
            total_success_count=10,
            total_wrong_count=2,
        )

        # 실행
        GameReportGenerationService._generate_game_report_advice(
            game_report=game_report,
            game=unknown_game,
        )

        # 검증 - 조언이 생성되지 않음
        advices = GameReportAdvice.objects.filter(game_report=game_report)
        self.assertEqual(advices.count(), 0)

    @patch("reports.services.game_report_generation_service.KidsTrafficGameReportAdviceGenerator")
    def test_generate_game_report_advice_deletes_existing(self, mock_generator_class):
        """기존 조언 삭제 후 새로 생성 테스트"""
        # Mock LLM generator
        mock_generator = Mock()
        mock_generator.generate_advice.return_value = [
            {
                "title": "새로운 조언",
                "description": "새로운 조언 내용",
            },
        ]
        mock_generator_class.return_value = mock_generator

        # 게임 레포트 및 기존 조언 생성
        game_report = GameReport.objects.create(
            report=self.report,
            game=self.game,
            total_plays_count=5,
            total_success_count=20,
            total_wrong_count=5,
        )

        old_advice = GameReportAdvice.objects.create(
            game_report=game_report,
            game=self.game,
            title="이전 조언",
            description="이전 조언 내용",
        )

        old_advice_id = old_advice.id

        # 실행
        GameReportGenerationService._generate_game_report_advice(
            game_report=game_report,
            game=self.game,
        )

        # 검증 - 이전 조언은 삭제되고 새로운 조언만 존재
        self.assertFalse(GameReportAdvice.objects.filter(id=old_advice_id).exists())

        advices = GameReportAdvice.objects.filter(game_report=game_report)
        self.assertEqual(advices.count(), 1)
        self.assertEqual(advices[0].title, "새로운 조언")

    def test_update_game_report_with_multiple_sessions(self):
        """여러 세션의 게임 결과 집계 테스트"""
        # 첫 번째 세션
        session1 = GameSession.objects.create(parent=self.user, game=self.game, child=self.child)
        GameResult.objects.create(
            child=self.child,
            game=self.game,
            session=session1,
            round_count=5,
            success_count=10,
            wrong_count=2,
            score=100,
        )

        # 두 번째 세션 (더 최신)
        session2 = GameSession.objects.create(parent=self.user, game=self.game, child=self.child)
        GameResult.objects.create(
            child=self.child,
            game=self.game,
            session=session2,
            round_count=7,
            success_count=14,
            wrong_count=1,
            score=100,
        )

        with patch.object(GameReportGenerationService, "_generate_game_report_advice"):
            # 실행
            game_report = GameReportGenerationService.update_or_create_game_report(
                report=self.report,
                game=self.game,
            )

            # 검증 - 모든 결과 집계
            self.assertEqual(game_report.total_plays_count, 2)
            self.assertEqual(game_report.total_play_rounds_count, 12)
            self.assertEqual(game_report.total_success_count, 24)
            self.assertEqual(game_report.total_wrong_count, 3)

            # 최신 세션으로 업데이트
            self.assertEqual(game_report.last_reflected_session_id, session2.id)
