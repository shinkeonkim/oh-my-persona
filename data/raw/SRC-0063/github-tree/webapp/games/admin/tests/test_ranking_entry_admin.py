from unittest.mock import MagicMock

from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.utils import timezone

import pytest
from games.admin import RankingEntryAdmin
from games.choices import GameCodeChoice, GameSessionStatusChoice
from games.models import Game, GameResult, GameSession, RankingEntry

from users.models import Child

User = get_user_model()


@pytest.mark.django_db
class RankingEntryAdminTests(TestCase):
    """RankingEntryAdmin 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.site = AdminSite()
        self.admin = RankingEntryAdmin(RankingEntry, self.site)
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

        # 게임 세션 및 결과 생성
        self.session = GameSession.objects.create(
            parent=self.user,
            child=self.child,
            game=self.game,
            status=GameSessionStatusChoice.COMPLETED,
        )

        self.game_result = GameResult.objects.create(
            session=self.session,
            child=self.child,
            game=self.game,
            score=85,
            wrong_count=2,
            round_count=10,
            success_count=8,
        )

        # 랭킹 엔트리 생성
        self.ranking = RankingEntry.objects.create(
            game_result=self.game_result,
            game=self.game,
            player_name="Test Player",
            organization="Test Org",
            score=85,
            round_count=10,
            contact_info="test@example.com",
        )

    def test_list_display(self):
        """list_display가 올바르게 설정되었는지 테스트"""
        expected_fields = (
            "rank_display",
            "player_name",
            "organization",
            "game_info",
            "score_display",
            "round_count",
            "event_highlight",
            "contact_info",
            "created_at",
        )
        self.assertEqual(self.admin.list_display, expected_fields)

    def test_search_fields(self):
        """search_fields가 올바르게 설정되었는지 테스트"""
        expected_fields = (
            "player_name",
            "organization",
            "game__name",
            "game__code",
            "contact_info",
        )
        self.assertEqual(self.admin.search_fields, expected_fields)

    def test_ordering(self):
        """ordering이 올바르게 설정되었는지 테스트"""
        expected_ordering = ("-score", "-round_count", "created_at")
        self.assertEqual(self.admin.ordering, expected_ordering)

    def test_rank_display_first_place(self):
        """rank_display가 1등을 올바르게 표시하는지 테스트"""
        result = self.admin.rank_display(self.ranking)

        # 금메달과 1등 표시
        self.assertIn("🥇", result)
        self.assertIn("#FFD700", result)  # Gold color

    def test_rank_display_second_place(self):
        """rank_display가 2등을 올바르게 표시하는지 테스트"""
        # 더 높은 점수의 랭킹 추가
        RankingEntry.objects.create(
            game_result=self.game_result,
            game=self.game,
            player_name="Higher Player",
            score=95,
            round_count=10,
        )

        result = self.admin.rank_display(self.ranking)

        # 은메달과 2등 표시
        self.assertIn("🥈", result)
        self.assertIn("#C0C0C0", result)  # Silver color

    def test_rank_display_third_place(self):
        """rank_display가 3등을 올바르게 표시하는지 테스트"""
        # 더 높은 점수의 랭킹 2개 추가
        RankingEntry.objects.create(
            game_result=self.game_result,
            game=self.game,
            player_name="First Player",
            score=95,
            round_count=10,
        )
        RankingEntry.objects.create(
            game_result=self.game_result,
            game=self.game,
            player_name="Second Player",
            score=90,
            round_count=10,
        )

        result = self.admin.rank_display(self.ranking)

        # 동메달과 3등 표시
        self.assertIn("🥉", result)
        self.assertIn("#CD7F32", result)  # Bronze color

    def test_game_info_display(self):
        """game_info가 올바르게 게임 정보를 표시하는지 테스트"""
        result = self.admin.game_info(self.ranking)

        # 게임 이름과 코드가 포함되어 있는지 확인
        self.assertIn(self.game.name, result)
        self.assertIn(self.game.code, result)

    def test_score_display_top_score(self):
        """score_display가 최고 점수를 올바르게 표시하는지 테스트"""
        result = self.admin.score_display(self.ranking)

        # 최고 점수는 금색 별 표시
        self.assertIn("⭐", result)
        self.assertIn("#FFD700", result)
        self.assertIn("85", result)

    def test_score_display_high_score(self):
        """score_display가 높은 점수를 올바르게 표시하는지 테스트"""
        # 더 높은 점수 추가
        RankingEntry.objects.create(
            game_result=self.game_result,
            game=self.game,
            player_name="Top Player",
            score=95,
            round_count=10,
        )

        result = self.admin.score_display(self.ranking)

        # 80점 이상은 초록색
        self.assertIn("#4CAF50", result)
        self.assertIn("85", result)

    def test_event_highlight_display(self):
        """event_highlight가 이벤트 하이라이트를 올바르게 표시하는지 테스트"""
        self.ranking.is_event_highlighted = True
        self.ranking.save()

        result = self.admin.event_highlight(self.ranking)

        # 이벤트 하이라이트 표시 확인
        self.assertIn("🎉", result)
        self.assertIn("최고점", result)

    def test_event_highlight_not_highlighted(self):
        """event_highlight가 하이라이트 없을 때 올바르게 표시하는지 테스트"""
        self.ranking.is_event_highlighted = False
        self.ranking.save()

        result = self.admin.event_highlight(self.ranking)

        # '-' 표시
        self.assertEqual(result, "-")

    def test_contact_info_display(self):
        """contact_info가 연락처를 올바르게 표시하는지 테스트"""
        result = self.admin.contact_info(self.ranking)

        self.assertEqual(result, "test@example.com")

    def test_contact_info_display_empty(self):
        """contact_info가 빈 연락처를 올바르게 표시하는지 테스트"""
        self.ranking.contact_info = None
        self.ranking.save()

        result = self.admin.contact_info(self.ranking)

        self.assertEqual(result, "-")

    def test_get_queryset_optimization(self):
        """get_queryset이 최적화되었는지 테스트"""
        request = self.factory.get("/admin/games/rankingentry/")
        request.user = self.superuser

        queryset = self.admin.get_queryset(request)

        # select_related와 annotate가 적용되었는지 확인
        ranking = queryset.first()
        self.assertIsNotNone(ranking)

        # rank와 top_score_in_game이 annotation으로 추가되었는지 확인
        self.assertTrue(hasattr(ranking, "rank"))
        self.assertTrue(hasattr(ranking, "top_score_in_game"))

    def test_formfield_for_foreignkey_game_result(self):
        """formfield_for_foreignkey가 game_result를 올바르게 필터링하는지 테스트"""
        request = self.factory.get("/admin/games/rankingentry/add/")
        request.user = self.superuser

        # 다른 게임 생성
        other_game = Game.objects.create(
            name="Other Game",
            code="OTHER",
            max_round=5,
            is_active=True,
        )

        other_session = GameSession.objects.create(
            parent=self.user,
            child=self.child,
            game=other_game,
            status=GameSessionStatusChoice.COMPLETED,
        )

        GameResult.objects.create(
            session=other_session,
            child=self.child,
            game=other_game,
            score=70,
            round_count=5,
        )

        # game_result 필드 formfield 가져오기
        game_result_field = RankingEntry._meta.get_field("game_result")
        formfield = self.admin.formfield_for_foreignkey(game_result_field, request)

        # BB_STAR와 KIDS_TRAFFIC 게임 결과만 포함되어야 함
        queryset = formfield.queryset
        game_codes = set(queryset.values_list("game__code", flat=True))

        self.assertIn(GameCodeChoice.BB_STAR, game_codes)
        self.assertNotIn("OTHER", game_codes)

    def test_clear_event_highlights_action(self):
        """clear_event_highlights 액션이 올바르게 동작하는지 테스트"""
        # 이벤트 하이라이트 설정
        self.ranking.is_event_highlighted = True
        self.ranking.event_triggered_at = timezone.now()
        self.ranking.save()

        request = self.factory.post("/admin/games/rankingentry/")
        request.user = self.superuser
        # Mock messages framework
        request._messages = MagicMock()

        queryset = RankingEntry.objects.filter(id=self.ranking.id)
        self.admin.clear_event_highlights(request, queryset)

        # 이벤트 하이라이트가 해제되었는지 확인
        self.ranking.refresh_from_db()
        self.assertFalse(self.ranking.is_event_highlighted)
        self.assertIsNone(self.ranking.event_triggered_at)

    def test_reset_rankings_action(self):
        """reset_rankings 액션이 올바르게 동작하는지 테스트"""
        request = self.factory.post("/admin/games/rankingentry/")
        request.user = self.superuser
        # Mock messages framework
        request._messages = MagicMock()

        queryset = RankingEntry.objects.filter(id=self.ranking.id)
        initial_count = RankingEntry.objects.count()

        self.admin.reset_rankings(request, queryset)

        # 랭킹이 삭제되었는지 확인
        final_count = RankingEntry.objects.count()
        self.assertEqual(final_count, initial_count - 1)

    def test_save_model_auto_fill_from_game_result(self):
        """save_model이 game_result에서 정보를 자동으로 채우는지 테스트"""
        request = self.factory.post("/admin/games/rankingentry/add/")
        request.user = self.superuser

        # 새 랭킹 엔트리 생성
        new_ranking = RankingEntry(
            game_result=self.game_result,
            player_name="New Player",
        )

        from django.forms import ModelForm

        class DummyForm(ModelForm):
            class Meta:
                model = RankingEntry
                fields = "__all__"

        form = DummyForm(instance=new_ranking)

        # save_model 호출
        self.admin.save_model(request, new_ranking, form, change=False)

        # game, score, round_count가 자동으로 채워졌는지 확인
        new_ranking.refresh_from_db()
        self.assertEqual(new_ranking.game, self.game_result.game)
        self.assertEqual(new_ranking.score, self.game_result.score)
        self.assertEqual(new_ranking.round_count, self.game_result.round_count)

    def test_save_model_auto_highlight_top_score(self):
        """save_model이 최고 점수에 자동으로 하이라이트를 설정하는지 테스트"""
        request = self.factory.post("/admin/games/rankingentry/add/")
        request.user = self.superuser

        # 더 높은 점수의 새 랭킹 엔트리 생성
        new_session = GameSession.objects.create(
            parent=self.user,
            child=self.child,
            game=self.game,
            status=GameSessionStatusChoice.COMPLETED,
        )

        new_result = GameResult.objects.create(
            session=new_session,
            child=self.child,
            game=self.game,
            score=95,
            round_count=10,
        )

        new_ranking = RankingEntry(
            game_result=new_result,
            player_name="Top Player",
        )

        from django.forms import ModelForm

        class DummyForm(ModelForm):
            class Meta:
                model = RankingEntry
                fields = "__all__"

        form = DummyForm(instance=new_ranking)

        # save_model 호출
        self.admin.save_model(request, new_ranking, form, change=False)

        # 새 랭킹이 하이라이트되었는지 확인
        new_ranking.refresh_from_db()
        self.assertTrue(new_ranking.is_event_highlighted)
        self.assertIsNotNone(new_ranking.event_triggered_at)

        # 기존 랭킹의 하이라이트가 해제되었는지 확인
        self.ranking.refresh_from_db()
        self.assertFalse(self.ranking.is_event_highlighted)

    def test_readonly_fields(self):
        """readonly_fields가 올바르게 설정되었는지 테스트"""
        expected_fields = (
            "game",
            "score",
            "round_count",
            "created_at",
            "updated_at",
        )
        self.assertEqual(self.admin.readonly_fields, expected_fields)

    def test_autocomplete_fields(self):
        """autocomplete_fields가 올바르게 설정되었는지 테스트"""
        expected_fields = ("game_result",)
        self.assertEqual(self.admin.autocomplete_fields, expected_fields)

    def test_actions_defined(self):
        """actions가 올바르게 정의되었는지 테스트"""
        expected_actions = ["clear_event_highlights", "reset_rankings"]
        self.assertEqual(self.admin.actions, expected_actions)

    def test_fieldsets_structure(self):
        """fieldsets 구조가 올바른지 테스트"""
        self.assertEqual(
            len(self.admin.fieldsets), 5
        )  # 5개: 게임결과선택, 참가자정보, 게임정보, 이벤트설정, 시스템정보

        # 게임 결과 선택
        result_selection = self.admin.fieldsets[0]
        self.assertEqual(result_selection[0], "게임 결과 선택")
        self.assertIn("game_result", result_selection[1]["fields"])

        # 참가자 정보
        player_info = self.admin.fieldsets[1]
        self.assertEqual(player_info[0], "참가자 정보")
        self.assertIn("player_name", player_info[1]["fields"])
        self.assertIn("organization", player_info[1]["fields"])
        self.assertIn("contact_info", player_info[1]["fields"])

    def test_date_hierarchy(self):
        """date_hierarchy가 올바르게 설정되었는지 테스트"""
        self.assertEqual(self.admin.date_hierarchy, "created_at")

    def test_multiple_rankings_ordering(self):
        """여러 랭킹이 올바르게 정렬되는지 테스트"""
        # 다양한 점수의 랭킹 추가
        RankingEntry.objects.create(
            game_result=self.game_result,
            game=self.game,
            player_name="Player 2",
            score=90,
            round_count=10,
        )
        RankingEntry.objects.create(
            game_result=self.game_result,
            game=self.game,
            player_name="Player 3",
            score=80,
            round_count=10,
        )

        request = self.factory.get("/admin/games/rankingentry/")
        request.user = self.superuser

        queryset = self.admin.get_queryset(request)

        # 점수 순으로 정렬되었는지 확인
        scores = list(queryset.values_list("score", flat=True))
        self.assertEqual(scores, sorted(scores, reverse=True))
