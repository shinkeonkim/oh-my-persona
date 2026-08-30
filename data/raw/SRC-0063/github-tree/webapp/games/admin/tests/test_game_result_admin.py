from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

import pytest
from games.admin import GameResultAdmin
from games.choices import GameCodeChoice, GameSessionStatusChoice
from games.models import Game, GameResult, GameSession

from users.models import Child

User = get_user_model()


@pytest.mark.django_db
class GameResultAdminTests(TestCase):
    """GameResultAdmin 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.site = AdminSite()
        self.admin = GameResultAdmin(GameResult, self.site)
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
            status=GameSessionStatusChoice.COMPLETED,
        )

        # 게임 결과 생성
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

    def test_list_display(self):
        """list_display가 올바르게 설정되었는지 테스트"""
        expected_fields = (
            "id",
            "child_info",
            "game_info",
            "score_display",
            "wrong_count",
            "success_count",
            "round_count",
            "reaction_time_avg",
            "session_id",
            "created_at",
        )
        self.assertEqual(self.admin.list_display, expected_fields)

    def test_search_fields(self):
        """search_fields가 올바르게 설정되었는지 테스트"""
        expected_fields = (
            "child__name",
            "game__name",
            "game__code",
            "session__id",
        )
        self.assertEqual(self.admin.search_fields, expected_fields)

    def test_ordering(self):
        """ordering이 올바르게 설정되었는지 테스트"""
        self.assertEqual(self.admin.ordering, ("-created_at",))

    def test_child_info_display(self):
        """child_info 메서드가 올바르게 자녀 정보를 표시하는지 테스트"""
        result = self.admin.child_info(self.result)

        # 자녀 이름이 포함되어 있는지 확인
        self.assertIn(self.child.name, result)

    def test_game_info_display(self):
        """game_info 메서드가 올바르게 게임 정보를 표시하는지 테스트"""
        result = self.admin.game_info(self.result)

        # 게임 이름과 코드가 포함되어 있는지 확인
        self.assertIn(self.game.name, result)
        self.assertIn(self.game.code, result)

    def test_score_display_high_score(self):
        """score_display 메서드가 높은 점수를 올바르게 표시하는지 테스트 (80점 이상)"""
        self.result.score = 90
        self.result.save()

        result = self.admin.score_display(self.result)

        # 초록색으로 표시되어야 함
        self.assertIn("#4CAF50", result)
        self.assertIn("90", result)

    def test_score_display_medium_score(self):
        """score_display 메서드가 중간 점수를 올바르게 표시하는지 테스트 (60-79점)"""
        self.result.score = 70
        self.result.save()

        result = self.admin.score_display(self.result)

        # 주황색으로 표시되어야 함
        self.assertIn("#FF9800", result)
        self.assertIn("70", result)

    def test_score_display_low_score(self):
        """score_display 메서드가 낮은 점수를 올바르게 표시하는지 테스트 (60점 미만)"""
        self.result.score = 50
        self.result.save()

        result = self.admin.score_display(self.result)

        # 빨간색으로 표시되어야 함
        self.assertIn("#F44336", result)
        self.assertIn("50", result)

    def test_reaction_time_avg_with_data(self):
        """reaction_time_avg 메서드가 평균 반응시간을 올바르게 계산하는지 테스트"""
        self.result.reaction_ms_sum = 5000
        self.result.round_count = 10
        self.result.save()

        result = self.admin.reaction_time_avg(self.result)

        # 500ms 평균이어야 함
        self.assertIn("500", result)
        self.assertIn("ms", result)

    def test_reaction_time_avg_without_data(self):
        """reaction_time_avg 메서드가 데이터 없을 때 올바르게 처리하는지 테스트"""
        self.result.reaction_ms_sum = None
        self.result.round_count = None
        self.result.save()

        result = self.admin.reaction_time_avg(self.result)

        # '-'가 표시되어야 함
        self.assertEqual(result, "-")

    def test_reaction_time_avg_with_zero_rounds(self):
        """reaction_time_avg 메서드가 라운드가 0일 때 올바르게 처리하는지 테스트"""
        self.result.reaction_ms_sum = 5000
        self.result.round_count = 0
        self.result.save()

        result = self.admin.reaction_time_avg(self.result)

        # '-'가 표시되어야 함 (0으로 나누기 방지)
        self.assertEqual(result, "-")

    def test_session_id_display(self):
        """session_id 메서드가 세션 ID를 짧게 표시하는지 테스트"""
        result = self.admin.session_id(self.result)

        # 처음 8자만 표시되어야 함
        session_id_str = str(self.session.id)
        self.assertIn(session_id_str[:8], result)
        self.assertIn("...", result)

    def test_get_queryset_optimization(self):
        """get_queryset이 select_related로 최적화되었는지 테스트"""
        request = self.factory.get("/admin/games/gameresult/")
        request.user = self.superuser

        queryset = self.admin.get_queryset(request)

        # select_related가 적용되었는지 확인 (쿼리 수 확인)
        with self.assertNumQueries(1):
            list(queryset)
            for result in queryset:
                # session, child, game에 접근해도 추가 쿼리가 발생하지 않아야 함
                _ = result.session.id
                _ = result.child.name
                _ = result.game.name

    def test_has_add_permission_false(self):
        """게임 결과 생성 권한이 없는지 테스트 (API를 통해서만 생성)"""
        request = self.factory.get("/admin/games/gameresult/")
        request.user = self.superuser

        self.assertFalse(self.admin.has_add_permission(request))

    def test_has_change_permission_false(self):
        """게임 결과 수정 권한이 없는지 테스트 (읽기 전용)"""
        request = self.factory.get(f"/admin/games/gameresult/{self.result.id}/change/")
        request.user = self.superuser

        self.assertFalse(self.admin.has_change_permission(request, self.result))

    def test_has_delete_permission_superuser(self):
        """슈퍼유저만 게임 결과 삭제 권한이 있는지 테스트"""
        request = self.factory.get(f"/admin/games/gameresult/{self.result.id}/delete/")
        request.user = self.superuser

        # 슈퍼유저는 삭제 가능
        self.assertTrue(self.admin.has_delete_permission(request, self.result))

    def test_has_delete_permission_staff(self):
        """일반 staff는 게임 결과 삭제 권한이 없는지 테스트"""
        request = self.factory.get(f"/admin/games/gameresult/{self.result.id}/delete/")
        request.user = self.staff_user

        # 일반 staff는 삭제 불가
        self.assertFalse(self.admin.has_delete_permission(request, self.result))

    def test_readonly_fields(self):
        """모든 필드가 readonly인지 테스트"""
        expected_readonly_fields = (
            "session",
            "child",
            "game",
            "score",
            "wrong_count",
            "reaction_ms_sum",
            "round_count",
            "success_count",
            "meta",
            "created_at",
            "updated_at",
        )
        self.assertEqual(self.admin.readonly_fields, expected_readonly_fields)

    def test_fieldsets_structure(self):
        """fieldsets 구조가 올바른지 테스트"""
        self.assertEqual(len(self.admin.fieldsets), 4)

        # 기본 정보
        basic_info = self.admin.fieldsets[0]
        self.assertEqual(basic_info[0], "기본 정보")
        self.assertIn("session", basic_info[1]["fields"])
        self.assertIn("child", basic_info[1]["fields"])
        self.assertIn("game", basic_info[1]["fields"])

        # 게임 결과
        result_info = self.admin.fieldsets[1]
        self.assertEqual(result_info[0], "게임 결과")
        self.assertIn("score", result_info[1]["fields"])
        self.assertIn("wrong_count", result_info[1]["fields"])
        self.assertIn("reaction_ms_sum", result_info[1]["fields"])

    def test_date_hierarchy(self):
        """date_hierarchy가 올바르게 설정되었는지 테스트"""
        self.assertEqual(self.admin.date_hierarchy, "created_at")

    def test_autocomplete_fields(self):
        """autocomplete_fields가 올바르게 설정되었는지 테스트"""
        expected_fields = ("session", "child", "game")
        self.assertEqual(self.admin.autocomplete_fields, expected_fields)

    def test_multiple_results_ordering(self):
        """여러 결과가 created_at 역순으로 정렬되는지 테스트"""
        # 추가 결과 생성
        import datetime

        from django.utils import timezone

        session2 = GameSession.objects.create(
            parent=self.user,
            child=self.child,
            game=self.game,
            status=GameSessionStatusChoice.COMPLETED,
        )

        result2 = GameResult.objects.create(
            session=session2,
            child=self.child,
            game=self.game,
            score=75,
            wrong_count=3,
            round_count=8,
            success_count=5,
        )
        result2.created_at = timezone.now() - datetime.timedelta(hours=1)
        result2.save()

        request = self.factory.get("/admin/games/gameresult/")
        request.user = self.superuser

        queryset = self.admin.get_queryset(request)

        # 최신 결과가 먼저 오는지 확인
        result_ids = list(queryset.values_list("id", flat=True))
        self.assertEqual(result_ids[0], self.result.id)
        self.assertEqual(result_ids[1], result2.id)
