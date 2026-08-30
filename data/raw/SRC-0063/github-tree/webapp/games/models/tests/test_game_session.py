import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

import pytest
from games.choices import GameCodeChoice, GameSessionStatusChoice
from games.models import Game, GameSession

from users.models import Child

User = get_user_model()


@pytest.mark.django_db
class GameSessionModelTests(TestCase):
    """GameSession 모델 테스트"""

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
            name="뿅뿅 아기별",
            code=GameCodeChoice.BB_STAR,
            max_round=10,
            is_active=True,
        )
        self.session = GameSession.objects.create(
            parent=self.user,
            child=self.child,
            game=self.game,
            status=GameSessionStatusChoice.STARTED,
        )

    def test_create_game_session(self):
        """게임 세션 생성 테스트"""
        session = GameSession.objects.create(
            parent=self.user,
            child=self.child,
            game=self.game,
            status=GameSessionStatusChoice.STARTED,
        )

        self.assertEqual(session.parent, self.user)
        self.assertEqual(session.child, self.child)
        self.assertEqual(session.game, self.game)
        self.assertEqual(session.status, GameSessionStatusChoice.STARTED)
        self.assertIsNotNone(session.id)
        self.assertIsInstance(session.id, uuid.UUID)

    def test_game_session_str(self):
        """게임 세션 __str__ 메서드 테스트"""
        expected = f"{self.child.name} - {self.game.name} (라운드 {self.session.current_round})"
        self.assertEqual(str(self.session), expected)

    def test_game_session_default_values(self):
        """게임 세션 기본값 테스트"""
        session = GameSession.objects.create(
            parent=self.user,
            child=self.child,
            game=self.game,
        )

        self.assertEqual(session.status, GameSessionStatusChoice.STARTED)
        self.assertEqual(session.current_round, 1)
        self.assertEqual(session.current_score, 0)
        self.assertIsNotNone(session.started_at)
        self.assertIsNone(session.ended_at)
        self.assertEqual(session.meta, {})

    def test_game_session_uuid_auto_generated(self):
        """게임 세션 UUID 자동 생성 테스트"""
        session1 = GameSession.objects.create(
            parent=self.user,
            child=self.child,
            game=self.game,
        )
        session2 = GameSession.objects.create(
            parent=self.user,
            child=self.child,
            game=self.game,
        )

        self.assertIsInstance(session1.id, uuid.UUID)
        self.assertIsInstance(session2.id, uuid.UUID)
        self.assertNotEqual(session1.id, session2.id)

    def test_game_session_status_change(self):
        """게임 세션 상태 변경 테스트"""
        self.assertEqual(self.session.status, GameSessionStatusChoice.STARTED)

        # 완료로 변경
        self.session.status = GameSessionStatusChoice.COMPLETED
        self.session.ended_at = timezone.now()
        self.session.save()

        self.session.refresh_from_db()
        self.assertEqual(self.session.status, GameSessionStatusChoice.COMPLETED)
        self.assertIsNotNone(self.session.ended_at)

    def test_game_session_current_round_update(self):
        """게임 세션 현재 라운드 업데이트 테스트"""
        self.assertEqual(self.session.current_round, 1)

        self.session.current_round = 5
        self.session.save()

        self.session.refresh_from_db()
        self.assertEqual(self.session.current_round, 5)

    def test_game_session_current_score_update(self):
        """게임 세션 현재 점수 업데이트 테스트"""
        self.assertEqual(self.session.current_score, 0)

        self.session.current_score = 85
        self.session.save()

        self.session.refresh_from_db()
        self.assertEqual(self.session.current_score, 85)

    def test_game_session_meta_data(self):
        """게임 세션 메타 데이터 테스트"""
        meta_data = {
            "round_details": [
                {"round": 1, "score": 10, "is_success": True},
                {"round": 2, "score": 15, "is_success": True},
            ]
        }

        self.session.meta = meta_data
        self.session.save()

        self.session.refresh_from_db()
        self.assertEqual(self.session.meta, meta_data)

    def test_game_session_related_name(self):
        """게임 세션 related_name 테스트"""
        # parent의 game_sessions
        sessions = self.user.game_sessions.all()
        self.assertIn(self.session, sessions)

        # child의 game_sessions
        sessions = self.child.game_sessions.all()
        self.assertIn(self.session, sessions)

        # game의 game_sessions
        sessions = self.game.game_sessions.all()
        self.assertIn(self.session, sessions)

    def test_game_session_cascade_delete_parent(self):
        """부모 삭제 시 세션도 삭제되는지 테스트"""
        session_id = self.session.id
        self.user.delete()

        with self.assertRaises(GameSession.DoesNotExist):
            GameSession.objects.get(id=session_id)

    def test_game_session_cascade_delete_child(self):
        """자녀 삭제 시 세션도 삭제되는지 테스트"""
        session_id = self.session.id
        self.child.delete()

        with self.assertRaises(GameSession.DoesNotExist):
            GameSession.objects.get(id=session_id)

    def test_game_session_cascade_delete_game(self):
        """게임 삭제 시 세션도 삭제되는지 테스트"""
        session_id = self.session.id
        self.game.delete()

        with self.assertRaises(GameSession.DoesNotExist):
            GameSession.objects.get(id=session_id)


@pytest.mark.django_db
class GameSessionManagerTests(TestCase):
    """GameSessionManager 테스트"""

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
            name="뿅뿅 아기별",
            code=GameCodeChoice.BB_STAR,
            max_round=10,
            is_active=True,
        )

        # 여러 상태의 세션 생성
        self.started_session = GameSession.objects.create(
            parent=self.user,
            child=self.child,
            game=self.game,
            status=GameSessionStatusChoice.STARTED,
        )
        self.completed_session = GameSession.objects.create(
            parent=self.user,
            child=self.child,
            game=self.game,
            status=GameSessionStatusChoice.COMPLETED,
        )
        self.forfeit_session = GameSession.objects.create(
            parent=self.user,
            child=self.child,
            game=self.game,
            status=GameSessionStatusChoice.FORFEIT,
        )

    def test_active_manager_method(self):
        """active() 매니저 메서드 테스트"""
        active_sessions = GameSession.objects.active()

        self.assertEqual(active_sessions.count(), 1)
        self.assertIn(self.started_session, active_sessions)
        self.assertNotIn(self.completed_session, active_sessions)
        self.assertNotIn(self.forfeit_session, active_sessions)

    def test_by_parent_manager_method(self):
        """by_parent() 매니저 메서드 테스트"""
        sessions = GameSession.objects.by_parent(self.user)

        self.assertEqual(sessions.count(), 3)
        self.assertIn(self.started_session, sessions)
        self.assertIn(self.completed_session, sessions)
        self.assertIn(self.forfeit_session, sessions)

    def test_by_parent_with_other_user(self):
        """다른 사용자의 세션 조회 테스트"""
        other_user = User.objects.create_user(
            username="otheruser",
            password="testpass123",
            email="other@example.com",
        )

        sessions = GameSession.objects.by_parent(other_user)
        self.assertEqual(sessions.count(), 0)

    def test_by_child_manager_method(self):
        """by_child() 매니저 메서드 테스트"""
        sessions = GameSession.objects.by_child(self.child)

        self.assertEqual(sessions.count(), 3)
        self.assertIn(self.started_session, sessions)
        self.assertIn(self.completed_session, sessions)
        self.assertIn(self.forfeit_session, sessions)

    def test_by_child_with_other_child(self):
        """다른 자녀의 세션 조회 테스트"""
        other_user = User.objects.create_user(
            username="otheruser",
            password="testpass123",
            email="other@example.com",
        )
        other_child = Child.objects.create(
            parent=other_user,
            name="Other Child",
            birth_year=2021,
            gender="F",
        )

        sessions = GameSession.objects.by_child(other_child)
        self.assertEqual(sessions.count(), 0)

    def test_filter_by_status(self):
        """상태별 필터링 테스트"""
        completed_sessions = GameSession.objects.filter(status=GameSessionStatusChoice.COMPLETED)

        self.assertEqual(completed_sessions.count(), 1)
        self.assertEqual(completed_sessions.first(), self.completed_session)

    def test_chaining_manager_methods(self):
        """매니저 메서드 체이닝 테스트"""
        # Manager 메서드는 체이닝이 안 되므로 filter 사용
        result = GameSession.objects.filter(parent=self.user, status=GameSessionStatusChoice.STARTED)

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first(), self.started_session)


@pytest.mark.django_db
class GameSessionMetaTests(TestCase):
    """GameSession 모델 메타 옵션 테스트"""

    def test_db_table_name(self):
        """DB 테이블 이름 테스트"""
        self.assertEqual(GameSession._meta.db_table, "game_sessions")

    def test_verbose_name(self):
        """verbose_name 테스트"""
        self.assertEqual(str(GameSession._meta.verbose_name), "게임 세션")

    def test_verbose_name_plural(self):
        """verbose_name_plural 테스트"""
        self.assertEqual(str(GameSession._meta.verbose_name_plural), "게임 세션")

    def test_ordering(self):
        """ordering 테스트"""
        self.assertEqual(GameSession._meta.ordering, ["-started_at"])

    def test_default_ordering_applied(self):
        """기본 정렬이 적용되는지 테스트"""
        user = User.objects.create_user(
            username="ordertest",
            password="testpass123",
            email="ordertest@example.com",
        )
        child = Child.objects.create(
            parent=user,
            name="Test Child",
            birth_year=2020,
            gender="M",
        )
        game = Game.objects.create(
            name="Test Game",
            code="TEST",
            max_round=10,
        )

        # 여러 세션 생성
        session1 = GameSession.objects.create(
            parent=user,
            child=child,
            game=game,
        )
        import time

        time.sleep(0.01)  # 약간의 시간차
        session2 = GameSession.objects.create(
            parent=user,
            child=child,
            game=game,
        )

        sessions = GameSession.objects.all()
        # 최신 것이 먼저 와야 함
        self.assertEqual(sessions[0], session2)
        self.assertEqual(sessions[1], session1)


@pytest.mark.django_db
class GameSessionFieldTests(TestCase):
    """GameSession 모델 필드 테스트"""

    def test_id_field_is_uuid(self):
        """id 필드가 UUID인지 테스트"""
        id_field = GameSession._meta.get_field("id")
        self.assertTrue(id_field.primary_key)
        self.assertEqual(id_field.default, uuid.uuid4)
        self.assertFalse(id_field.editable)

    def test_status_field_choices(self):
        """status 필드 choices 테스트"""
        status_field = GameSession._meta.get_field("status")
        self.assertEqual(status_field.choices, GameSessionStatusChoice.choices)

    def test_status_field_default(self):
        """status 필드 기본값 테스트"""
        status_field = GameSession._meta.get_field("status")
        self.assertEqual(status_field.default, GameSessionStatusChoice.STARTED)

    def test_current_round_default(self):
        """current_round 필드 기본값 테스트"""
        current_round_field = GameSession._meta.get_field("current_round")
        self.assertEqual(current_round_field.default, 1)

    def test_current_score_default(self):
        """current_score 필드 기본값 테스트"""
        current_score_field = GameSession._meta.get_field("current_score")
        self.assertEqual(current_score_field.default, 0)

    def test_started_at_auto_now_add(self):
        """started_at 필드 auto_now_add 테스트"""
        started_at_field = GameSession._meta.get_field("started_at")
        self.assertTrue(started_at_field.auto_now_add)

    def test_ended_at_nullable(self):
        """ended_at 필드 nullable 테스트"""
        ended_at_field = GameSession._meta.get_field("ended_at")
        self.assertTrue(ended_at_field.null)
        self.assertTrue(ended_at_field.blank)

    def test_meta_field_default(self):
        """meta 필드 기본값 테스트"""
        meta_field = GameSession._meta.get_field("meta")
        self.assertEqual(meta_field.default, dict)
        self.assertTrue(meta_field.null)
        self.assertTrue(meta_field.blank)

    def test_foreign_key_related_names(self):
        """ForeignKey related_name 테스트"""
        parent_field = GameSession._meta.get_field("parent")
        child_field = GameSession._meta.get_field("child")
        game_field = GameSession._meta.get_field("game")

        self.assertEqual(parent_field.remote_field.related_name, "game_sessions")
        self.assertEqual(child_field.remote_field.related_name, "game_sessions")
        self.assertEqual(game_field.remote_field.related_name, "game_sessions")
