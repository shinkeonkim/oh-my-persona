from django.contrib.auth import get_user_model
from django.test import TestCase

import pytest
from games.choices import GameCodeChoice
from games.models import Game
from rest_framework import status
from rest_framework.test import APIClient

from users.models import Child

User = get_user_model()


@pytest.mark.django_db
class GameListAPIViewTests(TestCase):
    """GameListAPIView 테스트"""

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
        self.url = "/api/v1/games/"

        # 게임 생성
        self.active_game1 = Game.objects.create(
            name="뿅뿅 아기별",
            code=GameCodeChoice.BB_STAR,
            max_round=10,
            is_active=True,
        )
        self.active_game2 = Game.objects.create(
            name="꼬마 교통지킴이",
            code=GameCodeChoice.KIDS_TRAFFIC,
            max_round=10,
            is_active=True,
        )
        # 비활성화된 게임
        self.inactive_game = Game.objects.create(
            name="Inactive Game",
            code="INACTIVE_GAME",
            max_round=5,
            is_active=False,
        )

    def test_get_active_games_success(self):
        """활성화된 게임 목록 조회 성공 테스트"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # 활성화된 게임 2개만 반환

        # 응답 데이터 확인
        game_codes = [game["code"] for game in response.data]
        self.assertIn(GameCodeChoice.BB_STAR, game_codes)
        self.assertIn(GameCodeChoice.KIDS_TRAFFIC, game_codes)
        self.assertNotIn("INACTIVE_GAME", game_codes)

    def test_get_active_games_ordering(self):
        """게임 목록이 ID 순으로 정렬되는지 테스트"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # ID 순으로 정렬되어 있는지 확인
        game_ids = [game["id"] for game in response.data]
        self.assertEqual(game_ids, sorted(game_ids))

    def test_get_active_games_response_structure(self):
        """응답 데이터 구조 확인 테스트"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 첫 번째 게임 데이터 구조 확인
        game_data = response.data[0]
        self.assertIn("id", game_data)
        self.assertIn("code", game_data)
        self.assertIn("name", game_data)
        self.assertIn("is_active", game_data)

    def test_get_active_games_without_authentication(self):
        """인증 없이 게임 목록 조회 실패 테스트"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_active_games_with_inactive_user(self):
        """비활성 사용자로 게임 목록 조회 실패 테스트"""
        inactive_user = User.objects.create_user(
            username="inactiveuser",
            password="testpass123",
            email="inactive@example.com",
            is_active=False,
        )
        self.client.force_authenticate(user=inactive_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_active_games_empty_list(self):
        """활성화된 게임이 없을 때 빈 목록 반환 테스트"""
        # 모든 게임 비활성화
        Game.objects.update(is_active=False)

        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_get_active_games_method_not_allowed(self):
        """GET 이외의 HTTP 메서드 사용 시 실패 테스트"""
        self.client.force_authenticate(user=self.user)

        # POST 요청
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # PUT 요청
        response = self.client.put(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # DELETE 요청
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
