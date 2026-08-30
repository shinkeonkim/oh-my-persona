from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

import pytest
from games.choices import GameCodeChoice, GameSessionStatusChoice
from games.models import Game, GameResult, GameSession

from users.models import Child

User = get_user_model()


@pytest.mark.django_db
class GameResultModelTests(TestCase):
    """GameResult 모델 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
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
            name="꼬마 교통지킴이",
            code=GameCodeChoice.KIDS_TRAFFIC,
            max_round=10,
            is_active=True,
        )
        self.session = GameSession.objects.create(
            parent=self.user,
            child=self.child,
            game=self.game,
            status=GameSessionStatusChoice.COMPLETED,
        )
        self.result = GameResult.objects.create(
            session=self.session,
            child=self.child,
            game=self.game,
            score=85,
            wrong_count=2,
            reaction_ms_sum=5000,
            round_count=10,
            success_count=8,
        )

    def test_create_game_result(self):
        """게임 결과 생성 테스트"""
        new_session = GameSession.objects.create(
            parent=self.user,
            child=self.child,
            game=self.game,
            status=GameSessionStatusChoice.COMPLETED,
        )

        result = GameResult.objects.create(
            session=new_session,
            child=self.child,
            game=self.game,
            score=90,
            wrong_count=1,
            reaction_ms_sum=4500,
            round_count=10,
            success_count=9,
        )

        self.assertEqual(result.session, new_session)
        self.assertEqual(result.child, self.child)
        self.assertEqual(result.game, self.game)
        self.assertEqual(result.score, 90)
        self.assertEqual(result.wrong_count, 1)
        self.assertEqual(result.reaction_ms_sum, 4500)
        self.assertEqual(result.round_count, 10)
        self.assertEqual(result.success_count, 9)

    def test_game_result_str(self):
        """게임 결과 __str__ 메서드 테스트"""
        id = self.result.id
        child_name = self.child.name
        game_name = self.game.name
        date = self.result.created_at.strftime("%Y-%m-%d %H:%M")
        expected = f"[{id}] {child_name} - {game_name} (점수: {self.result.score}) ({date})"
        self.assertEqual(str(self.result), expected)

    def test_game_result_required_fields(self):
        """게임 결과 필수 필드 테스트"""
        new_session = GameSession.objects.create(
            parent=self.user,
            child=self.child,
            game=self.game,
        )

        # score는 필수 필드
        result = GameResult.objects.create(
            session=new_session,
            child=self.child,
            game=self.game,
            score=75,
        )

        self.assertEqual(result.score, 75)
        self.assertEqual(result.wrong_count, 0)  # 기본값
        self.assertIsNone(result.reaction_ms_sum)
        self.assertIsNone(result.round_count)
        self.assertIsNone(result.success_count)

    def test_game_result_default_values(self):
        """게임 결과 기본값 테스트"""
        new_session = GameSession.objects.create(
            parent=self.user,
            child=self.child,
            game=self.game,
        )

        result = GameResult.objects.create(
            session=new_session,
            child=self.child,
            game=self.game,
            score=80,
        )

        self.assertEqual(result.wrong_count, 0)
        self.assertEqual(result.meta, {})

    def test_game_result_meta_data(self):
        """게임 결과 메타 데이터 테스트"""
        meta_data = {
            "round_details": [
                {
                    "round_number": 1,
                    "score": 10,
                    "wrong_count": 0,
                    "reaction_ms_sum": 500,
                    "is_success": True,
                },
                {
                    "round_number": 2,
                    "score": 15,
                    "wrong_count": 1,
                    "reaction_ms_sum": 600,
                    "is_success": True,
                },
            ]
        }

        self.result.meta = meta_data
        self.result.save()

        self.result.refresh_from_db()
        self.assertEqual(self.result.meta, meta_data)

    def test_game_result_unique_session_constraint(self):
        """세션당 하나의 결과만 생성 가능한지 테스트"""
        # 동일한 세션으로 두 번째 결과 생성 시도
        with self.assertRaises(IntegrityError):
            GameResult.objects.create(
                session=self.session,
                child=self.child,
                game=self.game,
                score=70,
            )

    def test_game_result_one_to_one_relationship(self):
        """세션과의 1:1 관계 테스트"""
        # session.result로 접근 가능
        self.assertEqual(self.session.result, self.result)

    def test_game_result_related_name(self):
        """게임 결과 related_name 테스트"""
        # child의 game_results
        results = self.child.game_results.all()
        self.assertIn(self.result, results)

        # game의 game_results
        results = self.game.game_results.all()
        self.assertIn(self.result, results)

    def test_game_result_cascade_delete_session(self):
        """세션 삭제 시 결과도 삭제되는지 테스트"""
        result_id = self.result.id
        self.session.delete()

        with self.assertRaises(GameResult.DoesNotExist):
            GameResult.objects.get(id=result_id)

    def test_game_result_cascade_delete_child(self):
        """자녀 삭제 시 결과도 삭제되는지 테스트"""
        result_id = self.result.id
        self.child.delete()

        with self.assertRaises(GameResult.DoesNotExist):
            GameResult.objects.get(id=result_id)

    def test_game_result_cascade_delete_game(self):
        """게임 삭제 시 결과도 삭제되는지 테스트"""
        result_id = self.result.id
        self.game.delete()

        with self.assertRaises(GameResult.DoesNotExist):
            GameResult.objects.get(id=result_id)

    def test_game_result_optional_fields(self):
        """선택적 필드들이 null일 수 있는지 테스트"""
        new_session = GameSession.objects.create(
            parent=self.user,
            child=self.child,
            game=self.game,
        )

        result = GameResult.objects.create(
            session=new_session,
            child=self.child,
            game=self.game,
            score=60,
            wrong_count=None,
            reaction_ms_sum=None,
            round_count=None,
            success_count=None,
            meta=None,
        )

        # wrong_count는 null=True이므로 None이 저장됨
        self.assertIsNone(result.wrong_count)
        self.assertIsNone(result.reaction_ms_sum)
        self.assertIsNone(result.round_count)
        self.assertIsNone(result.success_count)
        # meta는 명시적으로 None을 전달하면 None이 저장됨
        self.assertIsNone(result.meta)


@pytest.mark.django_db
class GameResultManagerTests(TestCase):
    """GameResultManager 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.user1 = User.objects.create_user(
            username="testuser1",
            password="testpass123",
            email="test1@example.com",
        )
        self.user2 = User.objects.create_user(
            username="testuser2",
            password="testpass123",
            email="test2@example.com",
        )
        self.child1 = Child.objects.create(
            parent=self.user1,
            name="Child 1",
            birth_year=2020,
            gender="M",
        )
        self.child2 = Child.objects.create(
            parent=self.user2,
            name="Child 2",
            birth_year=2021,
            gender="F",
        )
        self.game1 = Game.objects.create(
            name="Game 1",
            code=GameCodeChoice.BB_STAR,
            max_round=10,
        )
        self.game2 = Game.objects.create(
            name="Game 2",
            code=GameCodeChoice.KIDS_TRAFFIC,
            max_round=10,
        )

        # 여러 결과 생성
        session1 = GameSession.objects.create(
            parent=self.user1,
            child=self.child1,
            game=self.game1,
        )
        self.result1 = GameResult.objects.create(
            session=session1,
            child=self.child1,
            game=self.game1,
            score=85,
        )

        session2 = GameSession.objects.create(
            parent=self.user1,
            child=self.child1,
            game=self.game2,
        )
        self.result2 = GameResult.objects.create(
            session=session2,
            child=self.child1,
            game=self.game2,
            score=90,
        )

        session3 = GameSession.objects.create(
            parent=self.user2,
            child=self.child2,
            game=self.game1,
        )
        self.result3 = GameResult.objects.create(
            session=session3,
            child=self.child2,
            game=self.game1,
            score=75,
        )

    def test_by_child_manager_method(self):
        """by_child() 매니저 메서드 테스트"""
        results = GameResult.objects.by_child(self.child1)

        self.assertEqual(results.count(), 2)
        self.assertIn(self.result1, results)
        self.assertIn(self.result2, results)
        self.assertNotIn(self.result3, results)

    def test_by_game_manager_method(self):
        """by_game() 매니저 메서드 테스트"""
        results = GameResult.objects.by_game(self.game1)

        self.assertEqual(results.count(), 2)
        self.assertIn(self.result1, results)
        self.assertNotIn(self.result2, results)
        self.assertIn(self.result3, results)

    def test_chaining_manager_methods(self):
        """매니저 메서드 체이닝 테스트"""
        # Manager 메서드는 체이닝이 안 되므로 filter 사용
        results = GameResult.objects.filter(child=self.child1, game=self.game1)

        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.result1)

    def test_filter_by_score(self):
        """점수로 필터링 테스트"""
        high_score_results = GameResult.objects.filter(score__gte=85)

        self.assertEqual(high_score_results.count(), 2)
        self.assertIn(self.result1, high_score_results)
        self.assertIn(self.result2, high_score_results)

    def test_ordering_by_created_at(self):
        """생성 시간으로 정렬 테스트"""
        results = GameResult.objects.all()

        # 최신 것이 먼저 와야 함 (ordering = ["-created_at"])
        result_ids = [r.id for r in results]
        self.assertEqual(result_ids[0], self.result3.id)
        self.assertEqual(result_ids[1], self.result2.id)
        self.assertEqual(result_ids[2], self.result1.id)


@pytest.mark.django_db
class GameResultMetaTests(TestCase):
    """GameResult 모델 메타 옵션 테스트"""

    def test_db_table_name(self):
        """DB 테이블 이름 테스트"""
        self.assertEqual(GameResult._meta.db_table, "game_results")

    def test_verbose_name(self):
        """verbose_name 테스트"""
        self.assertEqual(str(GameResult._meta.verbose_name), "게임 결과")

    def test_verbose_name_plural(self):
        """verbose_name_plural 테스트"""
        self.assertEqual(str(GameResult._meta.verbose_name_plural), "게임 결과")

    def test_ordering(self):
        """ordering 테스트"""
        self.assertEqual(GameResult._meta.ordering, ["-created_at"])

    def test_unique_constraint_exists(self):
        """unique constraint 존재 확인"""
        constraints = GameResult._meta.constraints
        constraint_names = [constraint.name for constraint in constraints]

        self.assertIn("unique_session_result", constraint_names)


@pytest.mark.django_db
class GameResultFieldTests(TestCase):
    """GameResult 모델 필드 테스트"""

    def test_session_one_to_one_field(self):
        """session 필드가 OneToOneField인지 테스트"""
        session_field = GameResult._meta.get_field("session")
        self.assertTrue(session_field.one_to_one)
        self.assertEqual(session_field.remote_field.related_name, "result")

    def test_score_field_required(self):
        """score 필드가 필수인지 테스트"""
        score_field = GameResult._meta.get_field("score")
        self.assertFalse(score_field.null)
        self.assertFalse(score_field.blank)

    def test_wrong_count_field_default(self):
        """wrong_count 필드 기본값 테스트"""
        wrong_count_field = GameResult._meta.get_field("wrong_count")
        self.assertEqual(wrong_count_field.default, 0)

    def test_optional_fields_nullable(self):
        """선택적 필드들이 nullable인지 테스트"""
        reaction_ms_field = GameResult._meta.get_field("reaction_ms_sum")
        round_count_field = GameResult._meta.get_field("round_count")
        success_count_field = GameResult._meta.get_field("success_count")

        self.assertTrue(reaction_ms_field.null)
        self.assertTrue(round_count_field.null)
        self.assertTrue(success_count_field.null)

    def test_meta_field_default(self):
        """meta 필드 기본값 테스트"""
        meta_field = GameResult._meta.get_field("meta")
        self.assertEqual(meta_field.default, dict)
        self.assertTrue(meta_field.null)
        self.assertTrue(meta_field.blank)

    def test_foreign_key_related_names(self):
        """ForeignKey related_name 테스트"""
        child_field = GameResult._meta.get_field("child")
        game_field = GameResult._meta.get_field("game")

        self.assertEqual(child_field.remote_field.related_name, "game_results")
        self.assertEqual(game_field.remote_field.related_name, "game_results")

    def test_session_db_column(self):
        """session 필드의 db_column 테스트"""
        session_field = GameResult._meta.get_field("session")
        self.assertEqual(session_field.db_column, "session_id")
