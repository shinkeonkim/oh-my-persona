from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

import pytest
from games.admin import GameSessionAdmin
from games.choices import GameCodeChoice, GameSessionStatusChoice
from games.models import Game, GameSession

from users.models import Child

User = get_user_model()


@pytest.mark.django_db
class GameSessionAdminTests(TestCase):
    """GameSessionAdmin 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.site = AdminSite()
        self.admin = GameSessionAdmin(GameSession, self.site)
        self.factory = RequestFactory()

        # 슈퍼유저 생성
        self.superuser = User.objects.create_superuser(
            username="admin",
            password="admin123",
            email="admin@example.com",
        )

        # 일반 staff 유저 생성
        self.staff_user = User.objects.create_user(
            username="staff",
            password="staff123",
            email="staff@example.com",
            is_staff=True,
        )

        # 게임 사용자 및 자녀 생성
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

        # 게임 생성
        self.game = Game.objects.create(
            name="뿅뿅 아기별",
            code=GameCodeChoice.BB_STAR,
            max_round=10,
            is_active=True,
        )

        # 게임 세션 생성
        self.session = GameSession.objects.create(
            parent=self.user,
            child=self.child,
            game=self.game,
            status=GameSessionStatusChoice.STARTED,
            current_round=3,
            current_score=45,
        )

    def test_list_display(self):
        """list_display가 올바르게 설정되었는지 테스트"""
        expected_fields = (
            "id",
            "parent_info",
            "child_info",
            "game_info",
            "status_display",
            "current_round",
            "current_score",
            "started_at",
            "ended_at",
        )
        self.assertEqual(self.admin.list_display, expected_fields)

    def test_search_fields(self):
        """search_fields가 올바르게 설정되었는지 테스트"""
        expected_fields = (
            "id",
            "parent__email",
            "parent__username",
            "child__name",
            "game__name",
            "game__code",
        )
        self.assertEqual(self.admin.search_fields, expected_fields)

    def test_ordering(self):
        """ordering이 올바르게 설정되었는지 테스트"""
        self.assertEqual(self.admin.ordering, ("-started_at",))

    def test_parent_info_display(self):
        """parent_info 메서드가 올바르게 부모 정보를 표시하는지 테스트"""
        result = self.admin.parent_info(self.session)

        # HTML 형식으로 부모 정보가 포함되어 있는지 확인
        self.assertIn(self.user.username, result)
        self.assertIn(self.user.email, result)

    def test_child_info_display(self):
        """child_info 메서드가 올바르게 자녀 정보를 표시하는지 테스트"""
        result = self.admin.child_info(self.session)

        # 자녀 이름이 포함되어 있는지 확인
        self.assertIn(self.child.name, result)

    def test_game_info_display(self):
        """game_info 메서드가 올바르게 게임 정보를 표시하는지 테스트"""
        result = self.admin.game_info(self.session)

        # 게임 이름과 코드가 포함되어 있는지 확인
        self.assertIn(self.game.name, result)
        self.assertIn(self.game.code, result)

    def test_status_display_started(self):
        """status_display 메서드가 STARTED 상태를 올바르게 표시하는지 테스트"""
        result = self.admin.status_display(self.session)

        # STARTED 상태 색상 확인
        self.assertIn("#2196F3", result)  # Blue color for STARTED

    def test_status_display_completed(self):
        """status_display 메서드가 COMPLETED 상태를 올바르게 표시하는지 테스트"""
        self.session.status = GameSessionStatusChoice.COMPLETED
        self.session.save()

        result = self.admin.status_display(self.session)

        # COMPLETED 상태 색상 확인
        self.assertIn("#4CAF50", result)  # Green color for COMPLETED

    def test_status_display_forfeit(self):
        """status_display 메서드가 FORFEIT 상태를 올바르게 표시하는지 테스트"""
        self.session.status = GameSessionStatusChoice.FORFEIT
        self.session.save()

        result = self.admin.status_display(self.session)

        # FORFEIT 상태 색상 확인
        self.assertIn("#F44336", result)  # Red color for FORFEIT

    def test_get_queryset_optimization(self):
        """get_queryset이 select_related로 최적화되었는지 테스트"""
        request = self.factory.get("/admin/games/gamesession/")
        request.user = self.superuser

        queryset = self.admin.get_queryset(request)

        # select_related가 적용되었는지 확인 (쿼리 수 확인)
        with self.assertNumQueries(1):
            list(queryset)
            for session in queryset:
                # parent, child, game에 접근해도 추가 쿼리가 발생하지 않아야 함
                _ = session.parent.email
                _ = session.child.name
                _ = session.game.name

    def test_has_add_permission_false(self):
        """게임 세션 생성 권한이 없는지 테스트 (API를 통해서만 생성)"""
        request = self.factory.get("/admin/games/gamesession/")
        request.user = self.superuser

        self.assertFalse(self.admin.has_add_permission(request))

    def test_has_change_permission_false(self):
        """게임 세션 수정 권한이 없는지 테스트 (읽기 전용)"""
        request = self.factory.get(f"/admin/games/gamesession/{self.session.id}/change/")
        request.user = self.superuser

        self.assertFalse(self.admin.has_change_permission(request, self.session))

    def test_has_delete_permission_superuser(self):
        """슈퍼유저만 게임 세션 삭제 권한이 있는지 테스트"""
        request = self.factory.get(f"/admin/games/gamesession/{self.session.id}/delete/")
        request.user = self.superuser

        # 슈퍼유저는 삭제 가능
        self.assertTrue(self.admin.has_delete_permission(request, self.session))

    def test_has_delete_permission_staff(self):
        """일반 staff는 게임 세션 삭제 권한이 없는지 테스트"""
        request = self.factory.get(f"/admin/games/gamesession/{self.session.id}/delete/")
        request.user = self.staff_user

        # 일반 staff는 삭제 불가
        self.assertFalse(self.admin.has_delete_permission(request, self.session))

    def test_readonly_fields(self):
        """모든 필드가 readonly인지 테스트"""
        expected_readonly_fields = (
            "id",
            "parent",
            "child",
            "game",
            "status",
            "current_round",
            "current_score",
            "started_at",
            "ended_at",
            "meta",
            "created_at",
            "updated_at",
        )
        self.assertEqual(self.admin.readonly_fields, expected_readonly_fields)

    def test_fieldsets_structure(self):
        """fieldsets 구조가 올바른지 테스트"""
        self.assertEqual(len(self.admin.fieldsets), 4)

        # 세션 정보
        session_info = self.admin.fieldsets[0]
        self.assertEqual(session_info[0], "세션 정보")
        self.assertIn("parent", session_info[1]["fields"])
        self.assertIn("child", session_info[1]["fields"])
        self.assertIn("game", session_info[1]["fields"])
        self.assertIn("status", session_info[1]["fields"])

        # 진행 상황
        progress_info = self.admin.fieldsets[1]
        self.assertEqual(progress_info[0], "진행 상황")
        self.assertIn("current_round", progress_info[1]["fields"])
        self.assertIn("current_score", progress_info[1]["fields"])

    def test_date_hierarchy(self):
        """date_hierarchy가 올바르게 설정되었는지 테스트"""
        self.assertEqual(self.admin.date_hierarchy, "started_at")

    def test_autocomplete_fields(self):
        """autocomplete_fields가 올바르게 설정되었는지 테스트"""
        expected_fields = ("parent", "child", "game")
        self.assertEqual(self.admin.autocomplete_fields, expected_fields)

    def test_multiple_sessions_ordering(self):
        """여러 세션이 started_at 역순으로 정렬되는지 테스트"""
        # 추가 세션 생성
        import datetime

        from django.utils import timezone

        GameSession.objects.create(
            parent=self.user,
            child=self.child,
            game=self.game,
            status=GameSessionStatusChoice.STARTED,
            started_at=timezone.now() - datetime.timedelta(hours=1),
        )

        request = self.factory.get("/admin/games/gamesession/")
        request.user = self.superuser

        queryset = self.admin.get_queryset(request)

        # 최신 세션이 먼저 오는지 확인 (started_at 기준)
        sessions = list(queryset)
        started_at_times = [s.started_at for s in sessions]

        # started_at이 내림차순으로 정렬되어 있는지 확인
        self.assertEqual(started_at_times, sorted(started_at_times, reverse=True))
