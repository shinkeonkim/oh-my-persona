from django.contrib.auth import get_user_model
from django.test import TestCase

import pytest
from games.models import Game
from reports.models import GameReport, GameReportAdvice, Report

from users.models import Child

User = get_user_model()


@pytest.mark.django_db
class GameReportAdviceModelTests(TestCase):
    """GameReportAdvice 모델 테스트"""

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
        self.game_report = GameReport.objects.create(
            report=self.report,
            game=self.game,
        )

    def test_create_game_report_advice(self):
        """게임 레포트 조언 생성 테스트"""
        advice = GameReportAdvice.objects.create(
            game_report=self.game_report,
            game=self.game,
            title="집중력 향상 필요",
            description="아이의 집중력이 평균보다 낮습니다. 짧은 시간 동안 집중하는 연습이 필요합니다.",
        )

        self.assertEqual(advice.game_report, self.game_report)
        self.assertEqual(advice.game, self.game)
        self.assertEqual(advice.title, "집중력 향상 필요")
        self.assertIn("집중력", advice.description)
        self.assertIsNone(advice.error_message)

    def test_create_advice_with_error_message(self):
        """오류 메시지가 있는 조언 생성 테스트"""
        advice = GameReportAdvice.objects.create(
            game_report=self.game_report,
            game=self.game,
            title="조언 생성 실패",
            description="조언 생성 중 오류가 발생했습니다.",
            error_message="LLM API timeout",
        )

        self.assertEqual(advice.title, "조언 생성 실패")
        self.assertEqual(advice.error_message, "LLM API timeout")

    def test_multiple_advices_for_game_report(self):
        """하나의 게임 레포트에 여러 조언 생성 테스트"""
        advice1 = GameReportAdvice.objects.create(
            game_report=self.game_report,
            game=self.game,
            title="첫 번째 조언",
            description="첫 번째 조언 내용",
        )
        advice2 = GameReportAdvice.objects.create(
            game_report=self.game_report,
            game=self.game,
            title="두 번째 조언",
            description="두 번째 조언 내용",
        )
        advice3 = GameReportAdvice.objects.create(
            game_report=self.game_report,
            game=self.game,
            title="세 번째 조언",
            description="세 번째 조언 내용",
        )

        advices = GameReportAdvice.objects.filter(game_report=self.game_report)
        self.assertEqual(advices.count(), 3)
        self.assertIn(advice1, advices)
        self.assertIn(advice2, advices)
        self.assertIn(advice3, advices)

    def test_by_game_report_manager_method(self):
        """by_game_report 매니저 메서드 테스트"""
        advice1 = GameReportAdvice.objects.create(
            game_report=self.game_report,
            game=self.game,
            title="조언 1",
            description="내용 1",
        )
        advice2 = GameReportAdvice.objects.create(
            game_report=self.game_report,
            game=self.game,
            title="조언 2",
            description="내용 2",
        )

        # 다른 게임 레포트
        user2 = User.objects.create_user(username="user2", password="pass")
        child2 = Child.objects.create(
            parent=user2,
            name="Child 2",
            birth_year=2020,
            gender="M",
        )
        report2 = Report.objects.create(user=user2, child=child2)
        game_report2 = GameReport.objects.create(report=report2, game=self.game)
        GameReportAdvice.objects.create(
            game_report=game_report2,
            game=self.game,
            title="조언 3",
            description="내용 3",
        )

        advices = GameReportAdvice.objects.by_game_report(self.game_report)
        self.assertEqual(advices.count(), 2)
        self.assertIn(advice1, advices)
        self.assertIn(advice2, advices)

    def test_by_game_manager_method(self):
        """by_game 매니저 메서드 테스트"""
        advice1 = GameReportAdvice.objects.create(
            game_report=self.game_report,
            game=self.game,
            title="조언 1",
            description="내용 1",
        )

        # 다른 게임
        game2 = Game.objects.create(
            name="Game 2",
            code="GAME_2",
            max_round=5,
            is_active=True,
        )
        game_report2 = GameReport.objects.create(
            report=self.report,
            game=game2,
        )
        GameReportAdvice.objects.create(
            game_report=game_report2,
            game=game2,
            title="조언 2",
            description="내용 2",
        )

        advices = GameReportAdvice.objects.by_game(self.game)
        self.assertEqual(advices.count(), 1)
        self.assertIn(advice1, advices)

    def test_game_report_advice_str_representation(self):
        """게임 레포트 조언 문자열 표현 테스트"""
        advice = GameReportAdvice.objects.create(
            game_report=self.game_report,
            game=self.game,
            title="테스트 조언",
            description="테스트 내용",
        )

        expected = f"{self.game_report} - 테스트 조언"
        self.assertEqual(str(advice), expected)

    def test_advice_cascade_delete_with_game_report(self):
        """게임 레포트 삭제 시 조언도 함께 삭제되는지 테스트"""
        advice1 = GameReportAdvice.objects.create(
            game_report=self.game_report,
            game=self.game,
            title="조언 1",
            description="내용 1",
        )
        advice2 = GameReportAdvice.objects.create(
            game_report=self.game_report,
            game=self.game,
            title="조언 2",
            description="내용 2",
        )

        advice_ids = [advice1.id, advice2.id]

        # 게임 레포트 삭제
        self.game_report.delete()

        # 조언들도 삭제되었는지 확인
        for advice_id in advice_ids:
            self.assertFalse(GameReportAdvice.objects.filter(id=advice_id).exists())

    def test_advice_cascade_delete_with_game(self):
        """게임 삭제 시 조언도 함께 삭제되는지 테스트"""
        advice = GameReportAdvice.objects.create(
            game_report=self.game_report,
            game=self.game,
            title="조언",
            description="내용",
        )

        advice_id = advice.id

        # 게임 삭제
        self.game.delete()

        # 조언도 삭제되었는지 확인
        self.assertFalse(GameReportAdvice.objects.filter(id=advice_id).exists())

    def test_advice_ordering(self):
        """조언 정렬 테스트 (created_at 역순)"""
        advice1 = GameReportAdvice.objects.create(
            game_report=self.game_report,
            game=self.game,
            title="첫 번째",
            description="내용 1",
        )
        advice2 = GameReportAdvice.objects.create(
            game_report=self.game_report,
            game=self.game,
            title="두 번째",
            description="내용 2",
        )
        advice3 = GameReportAdvice.objects.create(
            game_report=self.game_report,
            game=self.game,
            title="세 번째",
            description="내용 3",
        )

        advices = GameReportAdvice.objects.filter(game_report=self.game_report)
        # created_at 역순이므로 최신이 먼저
        self.assertEqual(advices[0].id, advice3.id)
        self.assertEqual(advices[1].id, advice2.id)
        self.assertEqual(advices[2].id, advice1.id)

    def test_long_description(self):
        """긴 설명 텍스트 저장 테스트"""
        long_description = "a" * 5000  # 5000자

        advice = GameReportAdvice.objects.create(
            game_report=self.game_report,
            game=self.game,
            title="긴 조언",
            description=long_description,
        )

        advice.refresh_from_db()
        self.assertEqual(len(advice.description), 5000)
        self.assertEqual(advice.description, long_description)
