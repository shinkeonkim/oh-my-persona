from django.contrib.auth import get_user_model
from django.test import TestCase

import pytest
from games.choices import GameCodeChoice, GameSessionStatusChoice
from games.models import Game, GameResult, GameSession
from rest_framework import status
from rest_framework.test import APIClient

from users.models import Child

User = get_user_model()


@pytest.mark.django_db
class KidsTrafficStartAPIViewTests(TestCase):
    """KidsTrafficStartAPIView 테스트"""

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
        self.url = "/api/v1/games/kids-traffic/start/"

        # 꼬마 교통지킴이 게임 생성
        self.game = Game.objects.create(
            name="꼬마 교통지킴이",
            code=GameCodeChoice.KIDS_TRAFFIC,
            max_round=10,
            is_active=True,
        )

    def test_start_kids_traffic_game_success(self):
        """꼬마 교통지킴이 게임 시작 성공 테스트"""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("session_id", response.data)
        self.assertEqual(response.data["game_code"], GameCodeChoice.KIDS_TRAFFIC)
        self.assertEqual(response.data["status"], GameSessionStatusChoice.STARTED)
        self.assertIn("started_at", response.data)

        # DB에 세션이 생성되었는지 확인
        session = GameSession.objects.get(id=response.data["session_id"])
        self.assertEqual(session.parent, self.user)
        self.assertEqual(session.child, self.child)
        self.assertEqual(session.game, self.game)
        self.assertEqual(session.status, GameSessionStatusChoice.STARTED)

    def test_start_kids_traffic_game_without_authentication(self):
        """인증 없이 게임 시작 실패 테스트"""
        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_start_kids_traffic_game_without_child(self):
        """자녀 정보 없이 게임 시작 실패 테스트"""
        user_without_child = User.objects.create_user(
            username="usernochildren",
            password="testpass123",
            email="nochildren@example.com",
        )
        self.client.force_authenticate(user=user_without_child)

        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("등록된 자녀 정보가 없습니다", response.data["message"])

    def test_start_kids_traffic_game_with_inactive_game(self):
        """비활성화된 게임으로도 시작 가능 (현재 구현은 is_active를 체크하지 않음)"""
        self.game.is_active = False
        self.game.save()

        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.url, {}, format="json")

        # 현재 구현은 is_active를 체크하지 않으므로 201 반환
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("session_id", response.data)

    def test_start_kids_traffic_game_multiple_sessions(self):
        """동일 사용자가 여러 세션을 시작할 수 있는지 테스트"""
        self.client.force_authenticate(user=self.user)

        # 첫 번째 세션
        response1 = self.client.post(self.url, {}, format="json")
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        # 두 번째 세션
        response2 = self.client.post(self.url, {}, format="json")
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

        # 두 세션의 ID가 다른지 확인
        self.assertNotEqual(response1.data["session_id"], response2.data["session_id"])

        # DB에 두 개의 세션이 생성되었는지 확인
        sessions = GameSession.objects.filter(parent=self.user)
        self.assertEqual(sessions.count(), 2)


@pytest.mark.django_db
class KidsTrafficFinishAPIViewTests(TestCase):
    """KidsTrafficFinishAPIView 테스트"""

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
        self.url = "/api/v1/games/kids-traffic/finish/"

        # 꼬마 교통지킴이 게임 생성
        self.game = Game.objects.create(
            name="꼬마 교통지킴이",
            code=GameCodeChoice.KIDS_TRAFFIC,
            max_round=10,
            is_active=True,
        )

        # 게임 세션 생성
        self.session = GameSession.objects.create(
            parent=self.user,
            child=self.child,
            game=self.game,
            status=GameSessionStatusChoice.STARTED,
        )

    def test_finish_kids_traffic_game_success_with_reaction_time(self):
        """꼬마 교통지킴이 게임 종료 성공 테스트 (반응시간 포함)"""
        self.client.force_authenticate(user=self.user)

        data = {
            "session_id": str(self.session.id),
            "score": 90,
            "wrong_count": 1,
            "reaction_ms_sum": 5500,
            "round_count": 10,
            "success_count": 9,
            "meta": {
                "round_details": [
                    {
                        "round_number": 1,
                        "score": 10,
                        "wrong_count": 0,
                        "reaction_ms_sum": 500,
                        "is_success": True,
                        "time_limit_exceeded": False,
                    }
                ]
            },
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["session_id"], str(self.session.id))
        self.assertEqual(response.data["game_code"], GameCodeChoice.KIDS_TRAFFIC)
        self.assertEqual(response.data["score"], 90)
        self.assertEqual(response.data["wrong_count"], 1)
        self.assertEqual(response.data["reaction_ms_sum"], 5500)
        self.assertEqual(response.data["round_count"], 10)
        self.assertEqual(response.data["success_count"], 9)

        # DB에 게임 결과가 생성되었는지 확인
        result = GameResult.objects.get(session=self.session)
        self.assertEqual(result.score, 90)
        self.assertEqual(result.wrong_count, 1)
        self.assertEqual(result.reaction_ms_sum, 5500)
        self.assertEqual(result.round_count, 10)
        self.assertEqual(result.success_count, 9)

        # 세션이 완료 상태로 변경되었는지 확인
        self.session.refresh_from_db()
        self.assertEqual(self.session.status, GameSessionStatusChoice.COMPLETED)
        self.assertIsNotNone(self.session.ended_at)

    def test_finish_kids_traffic_game_success_without_reaction_time(self):
        """꼬마 교통지킴이 게임 종료 성공 테스트 (반응시간 없이)"""
        self.client.force_authenticate(user=self.user)

        data = {
            "session_id": str(self.session.id),
            "score": 75,
            "wrong_count": 3,
            "round_count": 8,
            "success_count": 5,
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["score"], 75)
        self.assertIsNone(response.data["reaction_ms_sum"])

    def test_finish_kids_traffic_game_minimal_data(self):
        """최소 데이터로 게임 종료 테스트"""
        self.client.force_authenticate(user=self.user)

        data = {
            "session_id": str(self.session.id),
            "score": 60,
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["score"], 60)
        self.assertEqual(response.data["wrong_count"], 0)  # 기본값
        self.assertIsNone(response.data["reaction_ms_sum"])

    def test_finish_kids_traffic_game_without_authentication(self):
        """인증 없이 게임 종료 실패 테스트"""
        data = {
            "session_id": str(self.session.id),
            "score": 90,
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_finish_kids_traffic_game_invalid_session_id(self):
        """잘못된 세션 ID로 게임 종료 실패 테스트"""
        self.client.force_authenticate(user=self.user)

        data = {
            "session_id": "00000000-0000-0000-0000-000000000000",
            "score": 90,
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("세션을 찾을 수 없거나 접근 권한이 없습니다", response.data["message"])

    def test_finish_kids_traffic_game_already_completed(self):
        """이미 완료된 세션으로 게임 종료 실패 테스트"""
        # 세션을 이미 완료 상태로 변경
        self.session.status = GameSessionStatusChoice.COMPLETED
        self.session.save()

        self.client.force_authenticate(user=self.user)

        data = {
            "session_id": str(self.session.id),
            "score": 90,
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn("이미 완료된 세션입니다", response.data["message"])

    def test_finish_kids_traffic_game_other_user_session(self):
        """다른 사용자의 세션으로 게임 종료 실패 테스트"""
        other_user = User.objects.create_user(
            username="otheruser",
            password="testpass123",
            email="other@example.com",
        )
        Child.objects.create(
            parent=other_user,
            name="Other Child",
            birth_year=2021,
            gender="F",
        )

        self.client.force_authenticate(user=other_user)

        data = {
            "session_id": str(self.session.id),
            "score": 90,
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_finish_kids_traffic_game_missing_score(self):
        """점수 없이 게임 종료 실패 테스트"""
        self.client.force_authenticate(user=self.user)

        data = {
            "session_id": str(self.session.id),
        }

        response = self.client.post(self.url, data, format="json")

        # DRF는 validation error에 대해 422 반환
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY])

    def test_finish_kids_traffic_game_with_meta(self):
        """메타 데이터와 함께 게임 종료 테스트"""
        self.client.force_authenticate(user=self.user)

        meta_data = {
            "round_details": [
                {
                    "round_number": 1,
                    "score": 10,
                    "wrong_count": 0,
                    "reaction_ms_sum": 450,
                    "is_success": True,
                    "time_limit_exceeded": False,
                },
                {
                    "round_number": 2,
                    "score": 10,
                    "wrong_count": 0,
                    "reaction_ms_sum": 550,
                    "is_success": True,
                    "time_limit_exceeded": False,
                },
            ]
        }

        data = {
            "session_id": str(self.session.id),
            "score": 20,
            "wrong_count": 0,
            "reaction_ms_sum": 1000,
            "round_count": 2,
            "success_count": 2,
            "meta": meta_data,
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["meta"], meta_data)

        result = GameResult.objects.get(session=self.session)
        self.assertEqual(result.meta, meta_data)
