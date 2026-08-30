from django.db import IntegrityError
from django.test import TestCase

import pytest
from games.choices import GameCodeChoice
from games.models import Game


@pytest.mark.django_db
class GameModelTests(TestCase):
    """Game 모델 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.game = Game.objects.create(
            name="뿅뿅 아기별",
            code=GameCodeChoice.BB_STAR,
            max_round=10,
            is_active=True,
        )

    def test_create_game(self):
        """게임 생성 테스트"""
        game = Game.objects.create(
            name="꼬마 교통지킴이",
            code=GameCodeChoice.KIDS_TRAFFIC,
            max_round=10,
            is_active=True,
        )

        self.assertEqual(game.name, "꼬마 교통지킴이")
        self.assertEqual(game.code, GameCodeChoice.KIDS_TRAFFIC)
        self.assertEqual(game.max_round, 10)
        self.assertTrue(game.is_active)

    def test_game_str(self):
        """게임 __str__ 메서드 테스트"""
        expected = f"{self.game.name} ({self.game.code})"
        self.assertEqual(str(self.game), expected)

    def test_game_code_unique_constraint(self):
        """게임 코드 유니크 제약조건 테스트"""
        with self.assertRaises(IntegrityError):
            Game.objects.create(
                name="중복 게임",
                code=GameCodeChoice.BB_STAR,  # 이미 존재하는 코드
                max_round=10,
            )

    def test_game_default_values(self):
        """게임 기본값 테스트"""
        game = Game.objects.create(
            name="테스트 게임",
            code="TEST_GAME",
        )

        self.assertEqual(game.max_round, 10)  # 기본값
        self.assertTrue(game.is_active)  # 기본값

    def test_game_max_round_value(self):
        """게임 최대 라운드 값 테스트"""
        game = Game.objects.create(
            name="라운드 테스트",
            code="ROUND_TEST",
            max_round=20,
        )

        self.assertEqual(game.max_round, 20)

    def test_game_is_active_flag(self):
        """게임 활성화 플래그 테스트"""
        # 활성화된 게임
        active_game = Game.objects.create(
            name="활성 게임",
            code="ACTIVE_GAME",
            is_active=True,
        )
        self.assertTrue(active_game.is_active)

        # 비활성화된 게임
        inactive_game = Game.objects.create(
            name="비활성 게임",
            code="INACTIVE_GAME",
            is_active=False,
        )
        self.assertFalse(inactive_game.is_active)


@pytest.mark.django_db
class GameManagerTests(TestCase):
    """GameManager 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        # 활성화된 게임
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
            name="비활성 게임",
            code="INACTIVE_GAME",
            max_round=5,
            is_active=False,
        )

    def test_active_manager_method(self):
        """active() 매니저 메서드 테스트"""
        active_games = Game.objects.active()

        self.assertEqual(active_games.count(), 2)
        self.assertIn(self.active_game1, active_games)
        self.assertIn(self.active_game2, active_games)
        self.assertNotIn(self.inactive_game, active_games)

    def test_by_code_manager_method(self):
        """by_code() 매니저 메서드 테스트"""
        bb_star_games = Game.objects.by_code(GameCodeChoice.BB_STAR)

        self.assertEqual(bb_star_games.count(), 1)
        self.assertEqual(bb_star_games.first(), self.active_game1)

    def test_by_code_with_filter_chain(self):
        """by_code()와 active() 체이닝 테스트"""
        # 활성화된 BB_STAR 게임 조회 (filter 사용)
        result = Game.objects.by_code(GameCodeChoice.BB_STAR).filter(is_active=True)

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first(), self.active_game1)

    def test_by_code_with_inactive_game(self):
        """비활성화된 게임도 by_code()로 조회 가능한지 테스트"""
        # 비활성 게임의 코드로 조회
        result = Game.objects.by_code("INACTIVE_GAME")

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first(), self.inactive_game)

    def test_by_code_nonexistent(self):
        """존재하지 않는 코드로 조회 테스트"""
        result = Game.objects.by_code("NONEXISTENT_GAME")

        self.assertEqual(result.count(), 0)

    def test_all_method(self):
        """all() 메서드로 모든 게임 조회 테스트"""
        all_games = Game.objects.all()

        self.assertEqual(all_games.count(), 3)
        self.assertIn(self.active_game1, all_games)
        self.assertIn(self.active_game2, all_games)
        self.assertIn(self.inactive_game, all_games)

    def test_filter_by_max_round(self):
        """max_round로 필터링 테스트"""
        games_with_10_rounds = Game.objects.filter(max_round=10)

        self.assertEqual(games_with_10_rounds.count(), 2)
        self.assertIn(self.active_game1, games_with_10_rounds)
        self.assertIn(self.active_game2, games_with_10_rounds)

    def test_ordering(self):
        """게임 정렬 테스트 (생성 시간 기준)"""
        games = Game.objects.all().order_by("id")

        # ID 순으로 정렬되어야 함
        game_ids = [game.id for game in games]
        self.assertEqual(game_ids, sorted(game_ids))


@pytest.mark.django_db
class GameMetaTests(TestCase):
    """Game 모델 메타 옵션 테스트"""

    def test_db_table_name(self):
        """DB 테이블 이름 테스트"""
        self.assertEqual(Game._meta.db_table, "games")

    def test_verbose_name(self):
        """verbose_name 테스트"""
        self.assertEqual(str(Game._meta.verbose_name), "게임")

    def test_verbose_name_plural(self):
        """verbose_name_plural 테스트"""
        self.assertEqual(str(Game._meta.verbose_name_plural), "게임")

    def test_unique_constraint_exists(self):
        """unique constraint 존재 확인"""
        constraints = Game._meta.constraints
        constraint_names = [constraint.name for constraint in constraints]

        self.assertIn("unique_game_code", constraint_names)


@pytest.mark.django_db
class GameFieldTests(TestCase):
    """Game 모델 필드 테스트"""

    def test_code_field_max_length(self):
        """code 필드 max_length 테스트"""
        code_field = Game._meta.get_field("code")
        self.assertEqual(code_field.max_length, 32)

    def test_name_field_max_length(self):
        """name 필드 max_length 테스트"""
        name_field = Game._meta.get_field("name")
        self.assertEqual(name_field.max_length, 100)

    def test_code_field_unique(self):
        """code 필드 unique 속성 테스트"""
        code_field = Game._meta.get_field("code")
        self.assertTrue(code_field.unique)

    def test_is_active_field_default(self):
        """is_active 필드 기본값 테스트"""
        is_active_field = Game._meta.get_field("is_active")
        self.assertTrue(is_active_field.default)

    def test_max_round_field_default(self):
        """max_round 필드 기본값 테스트"""
        max_round_field = Game._meta.get_field("max_round")
        self.assertEqual(max_round_field.default, 10)

    def test_code_field_choices(self):
        """code 필드 choices 테스트"""
        code_field = Game._meta.get_field("code")
        self.assertEqual(code_field.choices, GameCodeChoice.choices)

    def test_required_fields_not_null(self):
        """필수 필드 null 속성 테스트"""
        code_field = Game._meta.get_field("code")
        name_field = Game._meta.get_field("name")

        self.assertFalse(code_field.null)
        self.assertFalse(name_field.null)

    def test_required_fields_not_blank(self):
        """필수 필드 blank 속성 테스트"""
        code_field = Game._meta.get_field("code")
        name_field = Game._meta.get_field("name")

        self.assertFalse(code_field.blank)
        self.assertFalse(name_field.blank)
