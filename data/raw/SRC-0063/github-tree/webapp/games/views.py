from django.db.models import F, Window
from django.db.models.functions import Rank
from django.views.generic import TemplateView

from games.choices.game_code_choice import GameCodeChoice
from games.models import Game, RankingEntry
from rest_framework.response import Response
from rest_framework.views import APIView


class RankingDisplayView(TemplateView):
    """랭킹 화면 표시용 뷰"""

    template_name = "games/ranking_display.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 게임 정보 전달
        context["games"] = Game.objects.filter(code__in=[GameCodeChoice.BB_STAR, GameCodeChoice.KIDS_TRAFFIC]).values(
            "id", "name", "code"
        )
        return context


class RankingAPIView(APIView):
    """랭킹 데이터 API 뷰"""

    permission_classes = []  # 공개 API
    authentication_classes = []  # 인증 불필요

    def get(self, request):
        """게임별 랭킹 데이터 반환"""
        # BB_STAR 게임 랭킹
        bb_star_game = Game.objects.filter(code=GameCodeChoice.BB_STAR).first()
        bb_star_rankings = self._get_rankings(bb_star_game) if bb_star_game else []

        # KIDS_TRAFFIC 게임 랭킹
        kids_traffic_game = Game.objects.filter(code=GameCodeChoice.KIDS_TRAFFIC).first()
        kids_traffic_rankings = self._get_rankings(kids_traffic_game) if kids_traffic_game else []

        # 종합 랭킹 (모든 게임 합산)
        all_rankings = self._get_all_rankings()

        return Response(
            {
                "bb_star": bb_star_rankings,
                "kids_traffic": kids_traffic_rankings,
                "all": all_rankings,
                "updated_at": self._get_latest_update_time(),
            }
        )

    def _get_rankings(self, game):
        """특정 게임의 랭킹 조회"""
        if not game:
            return []

        queryset = (
            RankingEntry.objects.filter(game=game)
            .select_related("game")
            .annotate(
                rank=Window(
                    expression=Rank(),
                    order_by=[
                        F("score").desc(),
                        F("round_count").desc(),
                        F("created_at").asc(),
                    ],
                )
            )
            .order_by("rank")[:50]  # 상위 50명까지
        )

        return [
            {
                "rank": entry.rank,
                "player_name": entry.player_name,
                "organization": entry.organization or "",
                "score": entry.score,
                "round_count": entry.round_count or 0,
                "created_at": entry.created_at.isoformat(),
            }
            for entry in queryset
        ]

    def _get_all_rankings(self):
        """종합 랭킹 조회 (모든 게임)"""
        queryset = (
            RankingEntry.objects.all()
            .select_related("game")
            .annotate(
                rank=Window(
                    expression=Rank(),
                    order_by=[
                        F("score").desc(),
                        F("round_count").desc(),
                        F("created_at").asc(),
                    ],
                )
            )
            .order_by("rank")[:50]  # 상위 50명까지
        )

        return [
            {
                "rank": entry.rank,
                "player_name": entry.player_name,
                "organization": entry.organization or "",
                "score": entry.score,
                "round_count": entry.round_count or 0,
                "created_at": entry.created_at.isoformat(),
                "game_name": entry.game.name if entry.game else "-",
            }
            for entry in queryset
        ]

    def _get_latest_update_time(self):
        """가장 최근 업데이트 시각 조회"""
        latest_entry = RankingEntry.objects.order_by("-updated_at").first()
        return latest_entry.updated_at.isoformat() if latest_entry else None
