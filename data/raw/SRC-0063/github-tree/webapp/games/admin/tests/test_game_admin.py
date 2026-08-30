from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

import pytest
from games.admin import GameAdmin
from games.choices import GameCodeChoice
from games.models import Game

User = get_user_model()


@pytest.mark.django_db
class GameAdminTests(TestCase):
    """GameAdmin 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.site = AdminSite()
        self.admin = GameAdmin(Game, self.site)
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

        # 게임 생성
        self.game = Game.objects.create(
            name="뿅뿅 아기별",
            code=GameCodeChoice.BB_STAR,
            max_round=10,
            is_active=True,
        )

    def test_list_display(self):
        """list_display가 올바르게 설정되었는지 테스트"""
        expected_fields = (
            "id",
            "code",
            "name",
            "max_round",
            "is_active",
            "created_at",
            "updated_at",
        )
        self.assertEqual(self.admin.list_display, expected_fields)

    def test_list_filter(self):
        """list_filter가 올바르게 설정되었는지 테스트"""
        self.assertEqual(len(self.admin.list_filter), 4)
        self.assertIn("is_active", self.admin.list_filter)
        self.assertIn("created_at", self.admin.list_filter)
        self.assertIn("updated_at", self.admin.list_filter)

    def test_search_fields(self):
        """search_fields가 올바르게 설정되었는지 테스트"""
        expected_fields = ("code", "name")
        self.assertEqual(self.admin.search_fields, expected_fields)

    def test_ordering(self):
        """ordering이 올바르게 설정되었는지 테스트"""
        self.assertEqual(self.admin.ordering, ("id",))

    def test_readonly_fields(self):
        """readonly_fields가 올바르게 설정되었는지 테스트"""
        expected_fields = ("created_at", "updated_at")
        self.assertEqual(self.admin.readonly_fields, expected_fields)

    def test_fieldsets(self):
        """fieldsets가 올바르게 설정되었는지 테스트"""
        self.assertEqual(len(self.admin.fieldsets), 2)

        # 게임 정보 필드셋
        game_info = self.admin.fieldsets[0]
        self.assertEqual(game_info[0], "게임 정보")
        self.assertIn("code", game_info[1]["fields"])
        self.assertIn("name", game_info[1]["fields"])
        self.assertIn("max_round", game_info[1]["fields"])
        self.assertIn("is_active", game_info[1]["fields"])

        # 시스템 정보 필드셋
        system_info = self.admin.fieldsets[1]
        self.assertEqual(system_info[0], "시스템 정보")
        self.assertIn("created_at", system_info[1]["fields"])
        self.assertIn("updated_at", system_info[1]["fields"])
        self.assertIn("collapse", system_info[1]["classes"])

    def test_list_per_page(self):
        """list_per_page가 올바르게 설정되었는지 테스트"""
        self.assertEqual(self.admin.list_per_page, 25)

    def test_show_full_result_count(self):
        """show_full_result_count가 올바르게 설정되었는지 테스트"""
        self.assertTrue(self.admin.show_full_result_count)

    def test_has_add_permission(self):
        """게임 생성 권한이 있는지 테스트"""
        request = self.factory.get("/admin/games/game/")
        request.user = self.superuser

        # 기본적으로 생성 권한이 있어야 함
        self.assertTrue(self.admin.has_add_permission(request))

    def test_has_change_permission(self):
        """게임 수정 권한이 있는지 테스트"""
        request = self.factory.get(f"/admin/games/game/{self.game.id}/change/")
        request.user = self.superuser

        # 기본적으로 수정 권한이 있어야 함
        self.assertTrue(self.admin.has_change_permission(request, self.game))

    def test_has_delete_permission(self):
        """게임 삭제 권한이 있는지 테스트"""
        request = self.factory.get(f"/admin/games/game/{self.game.id}/delete/")
        request.user = self.superuser

        # 기본적으로 삭제 권한이 있어야 함
        self.assertTrue(self.admin.has_delete_permission(request, self.game))

    def test_queryset(self):
        """queryset이 올바르게 반환되는지 테스트"""
        # 여러 게임 생성
        Game.objects.create(
            name="꼬마 교통지킴이",
            code=GameCodeChoice.KIDS_TRAFFIC,
            max_round=10,
            is_active=True,
        )

        request = self.factory.get("/admin/games/game/")
        request.user = self.superuser

        queryset = self.admin.get_queryset(request)

        # 모든 게임이 반환되어야 함
        self.assertEqual(queryset.count(), 2)

    def test_game_ordering_by_id(self):
        """게임이 ID 순으로 정렬되는지 테스트"""
        # 여러 게임 생성
        game2 = Game.objects.create(
            name="꼬마 교통지킴이",
            code=GameCodeChoice.KIDS_TRAFFIC,
            max_round=10,
            is_active=True,
        )

        request = self.factory.get("/admin/games/game/")
        request.user = self.superuser

        queryset = self.admin.get_queryset(request)

        # ID 순으로 정렬되어야 함
        game_ids = list(queryset.values_list("id", flat=True))
        self.assertEqual(game_ids, [self.game.id, game2.id])
        self.assertTrue(game_ids == sorted(game_ids))

    def test_readonly_fields_in_form(self):
        """폼에서 readonly 필드가 수정 불가능한지 테스트"""
        request = self.factory.get(f"/admin/games/game/{self.game.id}/change/")
        request.user = self.superuser

        # created_at과 updated_at은 readonly여야 함
        self.assertIn("created_at", self.admin.readonly_fields)
        self.assertIn("updated_at", self.admin.readonly_fields)
