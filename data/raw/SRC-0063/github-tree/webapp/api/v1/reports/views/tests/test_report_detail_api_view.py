from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

import pytest
from games.choices import GameCodeChoice
from games.models import Game, GameResult, GameSession
from reports.models import GameReport, GameReportAdvice, Report, ReportPin
from rest_framework import status
from rest_framework.test import APIClient

from users.models import BotToken, Child

User = get_user_model()


@pytest.mark.django_db
class ReportDetailAPIViewTests(TestCase):
    """ReportDetailAPIView 테스트"""

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
            name="Kids Traffic",
            code=GameCodeChoice.KIDS_TRAFFIC,
            max_round=10,
            is_active=True,
        )
        self.url = "/api/v1/reports/"

        # 게임 결과 및 레포트 생성
        self.session = GameSession.objects.create(parent=self.user, game=self.game, child=self.child)
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

        self.report = Report.objects.create(
            user=self.user,
            child=self.child,
            concentration_score=75,
        )

        self.game_report = GameReport.objects.create(
            report=self.report,
            game=self.game,
            total_plays_count=1,
            total_success_count=10,
            total_wrong_count=2,
            last_reflected_session=self.session,
        )

        GameReportAdvice.objects.create(
            game_report=self.game_report,
            game=self.game,
            title="Test Advice",
            description="Test advice description",
        )

    def test_report_detail_jwt_auth_with_pin(self):
        """JWT 인증 + PIN 검증 성공 테스트"""
        # PIN 설정
        report_pin = ReportPin.objects.create(user=self.user)
        report_pin.pin_hash = report_pin.get_pin_hash("1234")
        report_pin.enabled_at = timezone.now()
        report_pin.save()

        self.client.force_authenticate(user=self.user)

        data = {"pin": "1234"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("id", response.data)
        self.assertIn("concentration_score", response.data)
        self.assertIn("game_reports", response.data)

    def test_report_detail_jwt_auth_wrong_pin(self):
        """JWT 인증 + 잘못된 PIN 테스트"""
        # PIN 설정
        report_pin = ReportPin.objects.create(user=self.user)
        report_pin.pin_hash = report_pin.get_pin_hash("1234")
        report_pin.enabled_at = timezone.now()
        report_pin.save()

        self.client.force_authenticate(user=self.user)

        data = {"pin": "9999"}  # 잘못된 PIN
        response = self.client.post(self.url, data, format="json")

        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY])

    def test_report_detail_jwt_auth_no_pin_set(self):
        """JWT 인증 + PIN이 설정되지 않은 경우 스킵 테스트"""
        self.client.force_authenticate(user=self.user)

        # PIN 없이 요청 (PIN이 설정되지 않았으므로 검증 스킵)
        data = {}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("id", response.data)

    def test_report_detail_jwt_auth_missing_pin_field(self):
        """JWT 인증 + PIN 설정되어 있지만 요청에 PIN 필드 없음 테스트"""
        # PIN 설정
        report_pin = ReportPin.objects.create(user=self.user)
        report_pin.pin_hash = report_pin.get_pin_hash("1234")
        report_pin.enabled_at = timezone.now()
        report_pin.save()

        self.client.force_authenticate(user=self.user)

        data = {}  # PIN 필드 없음
        response = self.client.post(self.url, data, format="json")

        # PIN이 설정되어 있으면 PIN 필드가 필수
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY])

    def test_report_detail_bot_auth_skips_pin(self):
        """Bot 인증 시 PIN 검증 스킵 테스트"""
        # BOT 토큰 생성
        bot_token = BotToken.create_for_report(self.user)

        # BOT 토큰으로 요청 (PIN 없이)
        response = self.client.post(
            self.url,
            data={},
            HTTP_X_BOT_TOKEN=bot_token.token,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("id", response.data)

    def test_report_detail_no_child(self):
        """자녀 정보가 없을 때 에러 테스트"""
        user_no_child = User.objects.create_user(
            username="nochilduser",
            password="testpass123",
            email="nochilduser@example.com",
        )
        self.client.force_authenticate(user=user_no_child)

        data = {}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_report_detail_no_report(self):
        """레포트가 없을 때 에러 테스트"""
        user2 = User.objects.create_user(
            username="user2",
            password="testpass123",
            email="user2@example.com",
        )
        Child.objects.create(
            parent=user2,
            name="Child 2",
            birth_year=2020,
            gender="F",
        )

        self.client.force_authenticate(user=user2)

        data = {}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_report_detail_requires_authentication(self):
        """인증 없이 요청 시 실패 테스트"""
        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_report_detail_response_structure(self):
        """응답 구조 검증 테스트"""
        self.client.force_authenticate(user=self.user)

        data = {}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 필수 필드 확인
        self.assertIn("id", response.data)
        self.assertIn("concentration_score", response.data)
        self.assertIn("game_reports", response.data)
        self.assertIn("created_at", response.data)
        self.assertIn("updated_at", response.data)

        # game_reports 구조 확인
        self.assertIsInstance(response.data["game_reports"], list)
        if len(response.data["game_reports"]) > 0:
            game_report = response.data["game_reports"][0]
            self.assertIn("id", game_report)
            self.assertIn("game_name", game_report)
            self.assertIn("game_code", game_report)
            self.assertIn("advices", game_report)

    def test_report_detail_includes_game_reports(self):
        """게임 레포트가 포함되는지 테스트"""
        self.client.force_authenticate(user=self.user)

        data = {}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["game_reports"]), 1)

        game_report = response.data["game_reports"][0]
        self.assertEqual(game_report["total_plays_count"], 1)
        self.assertEqual(game_report["total_success_count"], 10)

    def test_report_detail_includes_advices(self):
        """조언이 포함되는지 테스트"""
        self.client.force_authenticate(user=self.user)

        data = {}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        game_report = response.data["game_reports"][0]
        self.assertEqual(len(game_report["advices"]), 1)

        advice = game_report["advices"][0]
        self.assertEqual(advice["title"], "Test Advice")
        self.assertEqual(advice["description"], "Test advice description")

    def test_report_detail_prefetch_optimization(self):
        """prefetch_related가 올바르게 작동하는지 테스트"""
        self.client.force_authenticate(user=self.user)

        # 추가 게임 및 레포트 생성
        game2 = Game.objects.create(
            name="Game 2",
            code="GAME_2",
            max_round=5,
            is_active=True,
        )

        game_report2 = GameReport.objects.create(
            report=self.report,
            game=game2,
            total_plays_count=2,
            total_success_count=15,
            total_wrong_count=3,
            last_reflected_session=self.session,
        )

        GameReportAdvice.objects.create(
            game_report=game_report2,
            game=game2,
            title="Second Advice",
            description="Second advice description",
        )

        data = {}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["game_reports"]), 2)

    def test_report_detail_inactive_user(self):
        """비활성화된 사용자 요청 시 실패 테스트"""
        inactive_user = User.objects.create_user(
            username="inactive",
            password="testpass123",
            email="inactive@example.com",
            is_active=False,
        )
        self.client.force_authenticate(user=inactive_user)

        response = self.client.post(self.url, {}, format="json")

        # ActiveUserPermission에 의해 거부되어야 함
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_report_detail_pin_validation_short(self):
        """PIN이 너무 짧을 때 검증 테스트"""
        report_pin = ReportPin.objects.create(user=self.user)
        report_pin.pin_hash = report_pin.get_pin_hash("1234")
        report_pin.enabled_at = timezone.now()
        report_pin.save()

        self.client.force_authenticate(user=self.user)

        data = {"pin": "123"}  # 3자리 (최소 4자리 필요)
        response = self.client.post(self.url, data, format="json")

        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY])

    def test_report_detail_pin_validation_long(self):
        """PIN이 너무 길 때 검증 테스트"""
        report_pin = ReportPin.objects.create(user=self.user)
        report_pin.pin_hash = report_pin.get_pin_hash("123456")
        report_pin.enabled_at = timezone.now()
        report_pin.save()

        self.client.force_authenticate(user=self.user)

        data = {"pin": "1234567"}  # 7자리 (최대 6자리)
        response = self.client.post(self.url, data, format="json")

        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY])

    def test_report_detail_multiple_game_reports(self):
        """여러 게임 레포트 조회 테스트"""
        # 추가 게임 생성
        game2 = Game.objects.create(
            name="BB Star",
            code=GameCodeChoice.BB_STAR,
            max_round=8,
            is_active=True,
        )

        GameReport.objects.create(
            report=self.report,
            game=game2,
            total_plays_count=3,
            total_success_count=20,
            total_wrong_count=5,
            last_reflected_session=self.session,
        )

        self.client.force_authenticate(user=self.user)

        data = {}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["game_reports"]), 2)

    def test_report_detail_concentration_score(self):
        """집중력 점수가 포함되는지 테스트"""
        self.client.force_authenticate(user=self.user)

        data = {}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["concentration_score"], 75)

    def test_report_detail_bot_auth_with_header(self):
        """Bot 인증 시 X-BOT-TOKEN 헤더로 토큰 전달 테스트"""
        bot_token = BotToken.create_for_report(self.user)

        # X-BOT-TOKEN 헤더로 전달
        response = self.client.post(
            self.url,
            data={},
            format="json",
            headers={"X-BOT-TOKEN": bot_token.token},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("id", response.data)
