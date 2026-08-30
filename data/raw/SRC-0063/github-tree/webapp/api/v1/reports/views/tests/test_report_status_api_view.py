from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

import pytest
from games.choices import GameCodeChoice
from games.models import Game, GameResult, GameSession
from reports.choices import ReportStatusChoice
from reports.models import GameReport, Report
from rest_framework import status
from rest_framework.test import APIClient

from users.models import Child

User = get_user_model()


@pytest.mark.django_db
class ReportStatusAPIViewTests(TestCase):
    """ReportStatusAPIView 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com",
        )
        self.child = Child.objects.create(
            parent=self.user,
            name="Test Child",
            birth_year=2020,
            gender="M",
        )
        self.game = Game.objects.create(
            name="Test Game",
            code=GameCodeChoice.KIDS_TRAFFIC,
            max_round=10,
            is_active=True,
        )
        self.url = "/api/v1/reports/status/"

    def test_report_status_no_child(self):
        """자녀 정보가 없을 때 에러 테스트"""
        user_no_child = User.objects.create_user(
            username="nochilduser",
            password="testpass123",
            email="nochilduser@example.com",
        )
        self.client.force_authenticate(user=user_no_child)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch("reports.services.report_status_check_service.generate_report_task.delay")
    def test_report_status_creates_report_if_not_exists(self, mock_task):
        """레포트가 없을 때 자동 생성 테스트"""
        self.client.force_authenticate(user=self.user)

        # 게임 결과 생성
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

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 레포트가 생성되었는지 확인
        report = Report.objects.filter(user=self.user, child=self.child).first()
        self.assertIsNotNone(report)

        # 상태 확인
        self.assertIn("status", response.data)
        self.assertIn("description", response.data)

    def test_report_status_no_games_played(self):
        """게임을 플레이하지 않았을 때 상태 테스트"""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], ReportStatusChoice.NO_GAMES_PLAYED)

    @patch("reports.services.report_status_check_service.generate_report_task.delay")
    def test_report_status_triggers_generation(self, mock_task):
        """게임 플레이 후 레포트 생성 트리거 테스트"""
        self.client.force_authenticate(user=self.user)

        # 게임 결과 생성
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

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], ReportStatusChoice.GENERATING)

        # Celery task가 호출되었는지 확인
        mock_task.assert_called_once_with(
            user_id=self.user.id,
            child_id=self.child.id,
        )

    def test_report_status_completed(self):
        """레포트가 완료 상태일 때 테스트"""
        self.client.force_authenticate(user=self.user)

        # 게임 결과 및 레포트 생성
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

        report = Report.objects.create(
            user=self.user,
            child=self.child,
            status=ReportStatusChoice.COMPLETED,
        )

        GameReport.objects.create(
            report=report,
            game=self.game,
            last_reflected_session=session,
        )

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], ReportStatusChoice.COMPLETED)

    def test_report_status_requires_authentication(self):
        """인증 없이 요청 시 실패 테스트"""
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("reports.services.report_status_check_service.generate_report_task.delay")
    def test_report_status_skips_when_generating(self, mock_task):
        """이미 GENERATING 상태일 때 건너뛰기 테스트"""
        self.client.force_authenticate(user=self.user)

        # 게임 결과 생성
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

        # 이미 GENERATING 상태인 레포트 생성
        Report.objects.create(
            user=self.user,
            child=self.child,
            status=ReportStatusChoice.GENERATING,
        )

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], ReportStatusChoice.GENERATING)

        # task가 호출되지 않아야 함
        mock_task.assert_not_called()

    def test_report_status_response_structure(self):
        """응답 구조 검증 테스트"""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("status", response.data)
        self.assertIn("description", response.data)

    @patch("reports.services.report_status_check_service.generate_report_task.delay")
    def test_report_status_multiple_games(self, mock_task):
        """여러 게임 플레이 시 상태 테스트"""
        game2 = Game.objects.create(
            name="Game 2",
            code="GAME_2",
            max_round=5,
            is_active=True,
        )

        self.client.force_authenticate(user=self.user)

        # 각 게임에 대해 별도의 세션 생성
        session1 = GameSession.objects.create(parent=self.user, game=self.game, child=self.child)
        session2 = GameSession.objects.create(parent=self.user, game=game2, child=self.child)

        GameResult.objects.create(
            child=self.child,
            game=self.game,
            session=session1,
            round_count=5,
            success_count=10,
            wrong_count=2,
            score=100,
        )
        GameResult.objects.create(
            child=self.child,
            game=game2,
            session=session2,
            round_count=3,
            success_count=6,
            wrong_count=1,
            score=100,
        )

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 게임을 플레이했으므로 GENERATING 또는 COMPLETED 상태여야 함
        self.assertIn(response.data["status"], [ReportStatusChoice.GENERATING, ReportStatusChoice.COMPLETED])

    def test_report_status_inactive_user(self):
        """비활성화된 사용자 요청 시 실패 테스트"""
        inactive_user = User.objects.create_user(
            username="inactive",
            password="testpass123",
            email="inactive@example.com",
            is_active=False,
        )
        self.client.force_authenticate(user=inactive_user)

        response = self.client.post(self.url)

        # ActiveUserPermission에 의해 거부되어야 함
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch("reports.services.report_status_check_service.generate_report_task.delay")
    def test_report_status_error_state(self, mock_task):
        """레포트 생성 오류 상태 테스트"""
        mock_task.side_effect = Exception("Task error")

        self.client.force_authenticate(user=self.user)

        # 게임 결과 생성
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

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], ReportStatusChoice.ERROR)

    def test_report_status_get_or_create_idempotent(self):
        """여러 번 호출해도 레포트가 중복 생성되지 않는지 테스트"""
        self.client.force_authenticate(user=self.user)

        # 첫 번째 호출
        response1 = self.client.post(self.url)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        report1_id = Report.objects.get(user=self.user, child=self.child).id

        # 두 번째 호출
        response2 = self.client.post(self.url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        report2_id = Report.objects.get(user=self.user, child=self.child).id

        # 동일한 레포트여야 함
        self.assertEqual(report1_id, report2_id)

        # 레포트가 하나만 존재해야 함
        self.assertEqual(Report.objects.filter(user=self.user, child=self.child).count(), 1)
