from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

import pytest
from games.choices import GameCodeChoice, GameSessionStatusChoice
from games.models import Game, GameResult, GameSession, RankingEntry

from users.models import Child

User = get_user_model()


@pytest.mark.django_db
class RankingEntryModelTests(TestCase):
    """RankingEntry 모델 테스트"""

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
            status=GameSessionStatusChoice.COMPLETED,
        )
        self.game_result = GameResult.objects.create(
            session=self.session,
            child=self.child,
            game=self.game,
            score=85,
            round_count=10,
        )
        self.ranking = RankingEntry.objects.create(
            game=self.game,
            game_result=self.game_result,
            player_name="Test Player",
            organization="Test Org",
            score=85,
            round_count=10,
            contact_info="test@example.com",
        )

    def test_create_ranking_entry(self):
        """랭킹 엔트리 생성 테스트"""
        ranking = RankingEntry.objects.create(
            game=self.game,
            game_result=self.game_result,
            player_name="Player 2",
            score=90,
            round_count=10,
        )

        self.assertEqual(ranking.game, self.game)
        self.assertEqual(ranking.game_result, self.game_result)
        self.assertEqual(ranking.player_name, "Player 2")
        self.assertEqual(ranking.score, 90)
        self.assertEqual(ranking.round_count, 10)

    def test_ranking_entry_str(self):
        """랭킹 엔트리 __str__ 메서드 테스트"""
        expected = f"{self.ranking.player_name} - {self.game.name} (점수: {self.ranking.score})"
        self.assertEqual(str(self.ranking), expected)

    def test_ranking_entry_without_game_result(self):
        """game_result 없이 랭킹 엔트리 생성 테스트"""
        ranking = RankingEntry.objects.create(
            game=self.game,
            player_name="Manual Entry",
            score=75,
            round_count=8,
        )

        self.assertIsNone(ranking.game_result)
        self.assertEqual(ranking.player_name, "Manual Entry")
        self.assertEqual(ranking.score, 75)

    def test_ranking_entry_optional_fields(self):
        """선택적 필드 테스트"""
        ranking = RankingEntry.objects.create(
            game=self.game,
            player_name="Simple Player",
            score=80,
        )

        self.assertIsNone(ranking.round_count)
        self.assertIsNone(ranking.contact_info)
        self.assertIsNone(ranking.organization)
        self.assertFalse(ranking.is_event_highlighted)
        self.assertIsNone(ranking.event_triggered_at)

    def test_ranking_entry_with_organization(self):
        """소속 정보 포함 랭킹 엔트리 테스트"""
        ranking = RankingEntry.objects.create(
            game=self.game,
            player_name="Org Player",
            organization="Test University",
            score=88,
        )

        self.assertEqual(ranking.organization, "Test University")

    def test_ranking_entry_event_highlight(self):
        """이벤트 하이라이트 테스트"""
        self.assertFalse(self.ranking.is_event_highlighted)
        self.assertIsNone(self.ranking.event_triggered_at)

        # 하이라이트 설정
        self.ranking.is_event_highlighted = True
        self.ranking.event_triggered_at = timezone.now()
        self.ranking.save()

        self.ranking.refresh_from_db()
        self.assertTrue(self.ranking.is_event_highlighted)
        self.assertIsNotNone(self.ranking.event_triggered_at)

    def test_ranking_entry_related_name(self):
        """랭킹 엔트리 related_name 테스트"""
        # game의 ranking_entries
        entries = self.game.ranking_entries.all()
        self.assertIn(self.ranking, entries)

        # game_result의 ranking_entry
        self.assertEqual(self.game_result.ranking_entry.first(), self.ranking)

    def test_ranking_entry_cascade_delete_game(self):
        """게임 삭제 시 랭킹 엔트리도 삭제되는지 테스트"""
        ranking_id = self.ranking.id
        self.game.delete()

        with self.assertRaises(RankingEntry.DoesNotExist):
            RankingEntry.objects.get(id=ranking_id)

    def test_ranking_entry_set_null_on_game_result_delete(self):
        """game_result 삭제 시 SET_NULL 테스트"""
        self.assertIsNotNone(self.ranking.game_result)

        self.game_result.delete()

        self.ranking.refresh_from_db()
        self.assertIsNone(self.ranking.game_result)

    def test_ranking_entry_contact_info(self):
        """연락처 정보 테스트"""
        ranking = RankingEntry.objects.create(
            game=self.game,
            player_name="Contact Player",
            score=70,
            contact_info="player@example.com",
        )

        self.assertEqual(ranking.contact_info, "player@example.com")

    def test_ranking_entry_max_length_fields(self):
        """필드 최대 길이 테스트"""
        # player_name 최대 100자
        long_name = "A" * 100
        ranking = RankingEntry.objects.create(
            game=self.game,
            player_name=long_name,
            score=80,
        )
        self.assertEqual(len(ranking.player_name), 100)

        # organization 최대 30자
        long_org = "B" * 30
        ranking.organization = long_org
        ranking.save()
        self.assertEqual(len(ranking.organization), 30)


@pytest.mark.django_db
class RankingEntryManagerTests(TestCase):
    """RankingEntryManager 테스트"""

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

        # 여러 랭킹 엔트리 생성
        self.ranking1 = RankingEntry.objects.create(
            game=self.game1,
            player_name="Player 1",
            score=95,
            round_count=10,
        )
        self.ranking2 = RankingEntry.objects.create(
            game=self.game1,
            player_name="Player 2",
            score=85,
            round_count=10,
        )
        self.ranking3 = RankingEntry.objects.create(
            game=self.game1,
            player_name="Player 3",
            score=90,
            round_count=10,
        )
        self.ranking4 = RankingEntry.objects.create(
            game=self.game2,
            player_name="Player 4",
            score=88,
            round_count=10,
        )

    def test_by_game_manager_method(self):
        """by_game() 매니저 메서드 테스트"""
        entries = RankingEntry.objects.by_game(self.game1)

        self.assertEqual(entries.count(), 3)
        self.assertIn(self.ranking1, entries)
        self.assertIn(self.ranking2, entries)
        self.assertIn(self.ranking3, entries)
        self.assertNotIn(self.ranking4, entries)

    def test_top_scores_manager_method(self):
        """top_scores() 매니저 메서드 테스트"""
        top_entries = RankingEntry.objects.top_scores(self.game1, limit=2)

        self.assertEqual(len(top_entries), 2)
        # 점수 순으로 정렬되어야 함 (95, 90)
        self.assertEqual(top_entries[0], self.ranking1)
        self.assertEqual(top_entries[1], self.ranking3)

    def test_top_scores_ordering(self):
        """top_scores() 정렬 순서 테스트"""
        top_entries = RankingEntry.objects.top_scores(self.game1, limit=10)

        scores = [entry.score for entry in top_entries]
        # 점수가 내림차순으로 정렬되어야 함
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_top_scores_with_same_score(self):
        """동일 점수일 때 round_count로 정렬되는지 테스트"""
        # 동일 점수, 다른 라운드 수
        ranking5 = RankingEntry.objects.create(
            game=self.game1,
            player_name="Player 5",
            score=85,
            round_count=12,  # ranking2보다 높은 라운드
        )

        top_entries = RankingEntry.objects.top_scores(self.game1, limit=10)

        # 85점 중에서 round_count가 높은 것이 먼저 와야 함
        score_85_entries = [e for e in top_entries if e.score == 85]
        self.assertEqual(score_85_entries[0], ranking5)
        self.assertEqual(score_85_entries[1], self.ranking2)

    def test_get_top_score_manager_method(self):
        """get_top_score() 매니저 메서드 테스트"""
        top_score = RankingEntry.objects.get_top_score(self.game1)

        self.assertEqual(top_score, 95)

    def test_get_top_score_empty_game(self):
        """랭킹이 없는 게임의 top_score 테스트"""
        empty_game = Game.objects.create(
            name="Empty Game",
            code="EMPTY",
            max_round=10,
        )

        top_score = RankingEntry.objects.get_top_score(empty_game)

        self.assertEqual(top_score, 0)

    def test_default_ordering(self):
        """기본 정렬 테스트"""
        entries = RankingEntry.objects.filter(game=self.game1)

        # 점수 내림차순, 라운드 내림차순, 생성시간 오름차순
        scores = [entry.score for entry in entries]
        self.assertEqual(scores[0], 95)
        self.assertEqual(scores[1], 90)
        self.assertEqual(scores[2], 85)

    def test_top_scores_limit_parameter(self):
        """top_scores() limit 파라미터 테스트"""
        # limit=1
        top_1 = RankingEntry.objects.top_scores(self.game1, limit=1)
        self.assertEqual(len(top_1), 1)
        self.assertEqual(top_1[0], self.ranking1)

        # limit=3
        top_3 = RankingEntry.objects.top_scores(self.game1, limit=3)
        self.assertEqual(len(top_3), 3)

    def test_by_game_with_ordering(self):
        """by_game()로 조회 시 기본 정렬 적용 테스트"""
        entries = RankingEntry.objects.by_game(self.game1)

        # 첫 번째는 최고 점수여야 함
        self.assertEqual(entries.first(), self.ranking1)


@pytest.mark.django_db
class RankingEntryMetaTests(TestCase):
    """RankingEntry 모델 메타 옵션 테스트"""

    def test_db_table_name(self):
        """DB 테이블 이름 테스트"""
        self.assertEqual(RankingEntry._meta.db_table, "ranking_entries")

    def test_verbose_name(self):
        """verbose_name 테스트"""
        self.assertEqual(str(RankingEntry._meta.verbose_name), "랭킹 엔트리")

    def test_verbose_name_plural(self):
        """verbose_name_plural 테스트"""
        self.assertEqual(str(RankingEntry._meta.verbose_name_plural), "랭킹 엔트리")

    def test_ordering(self):
        """ordering 테스트"""
        expected_ordering = ["-score", "-round_count", "created_at"]
        self.assertEqual(RankingEntry._meta.ordering, expected_ordering)

    def test_indexes_exist(self):
        """인덱스 존재 확인"""
        indexes = RankingEntry._meta.indexes
        self.assertTrue(len(indexes) > 0)

        # game과 score에 대한 인덱스 확인
        index_fields = []
        for index in indexes:
            # index.fields는 문자열 리스트일 수 있음
            for field in index.fields:
                if isinstance(field, str):
                    index_fields.append(field)
                else:
                    index_fields.append(field.name)

        # "-" 제거하여 필드명만 확인
        clean_fields = [str(f).replace("-", "") for f in index_fields]
        self.assertIn("game", clean_fields)


@pytest.mark.django_db
class RankingEntryFieldTests(TestCase):
    """RankingEntry 모델 필드 테스트"""

    def test_player_name_field_max_length(self):
        """player_name 필드 max_length 테스트"""
        field = RankingEntry._meta.get_field("player_name")
        self.assertEqual(field.max_length, 100)

    def test_organization_field_max_length(self):
        """organization 필드 max_length 테스트"""
        field = RankingEntry._meta.get_field("organization")
        self.assertEqual(field.max_length, 30)

    def test_contact_info_field_max_length(self):
        """contact_info 필드 max_length 테스트"""
        field = RankingEntry._meta.get_field("contact_info")
        self.assertEqual(field.max_length, 200)

    def test_required_fields(self):
        """필수 필드 테스트"""
        game_field = RankingEntry._meta.get_field("game")
        player_name_field = RankingEntry._meta.get_field("player_name")
        score_field = RankingEntry._meta.get_field("score")

        self.assertFalse(game_field.null)
        self.assertFalse(player_name_field.null)
        self.assertFalse(score_field.null)

    def test_optional_fields(self):
        """선택적 필드 테스트"""
        game_result_field = RankingEntry._meta.get_field("game_result")
        round_count_field = RankingEntry._meta.get_field("round_count")
        contact_info_field = RankingEntry._meta.get_field("contact_info")
        organization_field = RankingEntry._meta.get_field("organization")

        self.assertTrue(game_result_field.null or game_result_field.blank)
        self.assertTrue(round_count_field.null or round_count_field.blank)
        self.assertTrue(contact_info_field.null or contact_info_field.blank)
        self.assertTrue(organization_field.null or organization_field.blank)

    def test_is_event_highlighted_default(self):
        """is_event_highlighted 필드 기본값 테스트"""
        field = RankingEntry._meta.get_field("is_event_highlighted")
        self.assertFalse(field.default)

    def test_event_triggered_at_nullable(self):
        """event_triggered_at 필드 nullable 테스트"""
        field = RankingEntry._meta.get_field("event_triggered_at")
        self.assertTrue(field.null)
        self.assertTrue(field.blank)

    def test_game_result_set_null(self):
        """game_result 필드 SET_NULL 속성 테스트"""
        game_result_field = RankingEntry._meta.get_field("game_result")
        from django.db.models import SET_NULL

        self.assertEqual(game_result_field.remote_field.on_delete, SET_NULL)

    def test_foreign_key_related_names(self):
        """ForeignKey related_name 테스트"""
        game_field = RankingEntry._meta.get_field("game")
        game_result_field = RankingEntry._meta.get_field("game_result")

        self.assertEqual(game_field.remote_field.related_name, "ranking_entries")
        self.assertEqual(game_result_field.remote_field.related_name, "ranking_entry")


@pytest.mark.django_db
class RankingEntryOrderingTests(TestCase):
    """RankingEntry 정렬 로직 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.game = Game.objects.create(
            name="Test Game",
            code="TEST",
            max_round=10,
        )

    def test_ordering_by_score_descending(self):
        """점수 내림차순 정렬 테스트"""
        ranking1 = RankingEntry.objects.create(
            game=self.game,
            player_name="Player 1",
            score=70,
        )
        ranking2 = RankingEntry.objects.create(
            game=self.game,
            player_name="Player 2",
            score=90,
        )
        ranking3 = RankingEntry.objects.create(
            game=self.game,
            player_name="Player 3",
            score=80,
        )

        entries = RankingEntry.objects.all()

        self.assertEqual(entries[0], ranking2)  # 90점
        self.assertEqual(entries[1], ranking3)  # 80점
        self.assertEqual(entries[2], ranking1)  # 70점

    def test_ordering_by_round_count_when_same_score(self):
        """동일 점수일 때 라운드 수로 정렬 테스트"""
        ranking1 = RankingEntry.objects.create(
            game=self.game,
            player_name="Player 1",
            score=80,
            round_count=8,
        )
        ranking2 = RankingEntry.objects.create(
            game=self.game,
            player_name="Player 2",
            score=80,
            round_count=10,
        )
        ranking3 = RankingEntry.objects.create(
            game=self.game,
            player_name="Player 3",
            score=80,
            round_count=9,
        )

        entries = RankingEntry.objects.all()

        # 동일 점수일 때 round_count가 높은 순
        self.assertEqual(entries[0], ranking2)  # 10 라운드
        self.assertEqual(entries[1], ranking3)  # 9 라운드
        self.assertEqual(entries[2], ranking1)  # 8 라운드

    def test_ordering_by_created_at_when_same_score_and_round(self):
        """동일 점수, 동일 라운드일 때 생성 시간으로 정렬 테스트"""
        import time

        ranking1 = RankingEntry.objects.create(
            game=self.game,
            player_name="Player 1",
            score=80,
            round_count=10,
        )
        time.sleep(0.01)
        ranking2 = RankingEntry.objects.create(
            game=self.game,
            player_name="Player 2",
            score=80,
            round_count=10,
        )
        time.sleep(0.01)
        ranking3 = RankingEntry.objects.create(
            game=self.game,
            player_name="Player 3",
            score=80,
            round_count=10,
        )

        entries = RankingEntry.objects.all()

        # 동일 점수, 동일 라운드일 때 먼저 생성된 순
        self.assertEqual(entries[0], ranking1)
        self.assertEqual(entries[1], ranking2)
        self.assertEqual(entries[2], ranking3)
