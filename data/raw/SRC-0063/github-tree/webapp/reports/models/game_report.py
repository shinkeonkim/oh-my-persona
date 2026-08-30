from django.db import models
from django.db.models import Count, Sum
from django.utils.translation import gettext_lazy as _

from games.choices import GameCodeChoice
from games.models import GameResult

from common.models import BaseModel, BaseModelManager


class GameReportManager(BaseModelManager):
    def by_report(self, report):
        return self.filter(report=report)

    def by_game(self, game):
        return self.filter(game=game)

    def get_or_create_for_report_and_game(self, report, game):
        """레포트와 게임에 대한 게임 레포트 조회 또는 생성"""
        game_report, created = self.get_or_create(
            report=report,
            game=game,
        )
        return game_report, created


class GameReport(BaseModel):
    """
    게임별 레포트 모델
    특정 레포트 내의 각 게임에 대한 결과 및 분석
    """

    class Meta:
        db_table = "game_reports"
        verbose_name = _("게임 레포트")
        verbose_name_plural = _("게임 레포트")
        constraints = [
            models.UniqueConstraint(
                fields=["report", "game"],
                name="unique_report_game",
            ),
        ]
        ordering = ["-updated_at"]

    objects = GameReportManager()

    report = models.ForeignKey(
        "reports.Report",
        on_delete=models.CASCADE,
        related_name="game_reports",
        null=False,
        blank=False,
        verbose_name=_("레포트"),
    )
    game = models.ForeignKey(
        "games.Game",
        on_delete=models.CASCADE,
        related_name="game_reports",
        null=False,
        blank=False,
        verbose_name=_("게임"),
    )
    last_reflected_session = models.ForeignKey(
        "games.GameSession",
        on_delete=models.SET_NULL,
        related_name="reflected_in_game_reports",
        null=True,
        blank=True,
        verbose_name=_("마지막 반영 세션"),
        help_text="가장 최근 반영된 게임 세션",
    )
    meta = models.JSONField(
        null=True,
        blank=True,
        verbose_name=_("메타 정보"),
        help_text="게임 결과를 추합한 게임과 관련된 추가 메타 정보",
    )

    # 통계 컬럼들
    total_plays_count = models.IntegerField(
        default=0,
        verbose_name=_("전체 플레이 횟수"),
        help_text="GameResult의 개수",
    )
    total_play_rounds_count = models.IntegerField(
        default=0,
        verbose_name=_("전체 플레이 라운드 수"),
        help_text="GameResult의 round_count 합",
    )
    max_rounds_count = models.IntegerField(
        default=0,
        verbose_name=_("최대 도달 라운드 횟수"),
        help_text="game의 max_round와 round_count가 같은 경우의 수",
    )
    total_reaction_ms_sum = models.BigIntegerField(
        default=0,
        verbose_name=_("총 반응시간 합계"),
        help_text="reaction_ms_sum 누적값 (밀리초)",
    )
    total_play_actions_count = models.IntegerField(
        default=0,
        verbose_name=_("전체 플레이 액션 수"),
        help_text="success_count + wrong_count",
    )
    total_success_count = models.IntegerField(
        default=0,
        verbose_name=_("전체 성공 횟수"),
        help_text="success_count 누적",
    )
    total_wrong_count = models.IntegerField(
        default=0,
        verbose_name=_("전체 오답 횟수"),
        help_text="wrong_count 누적",
    )

    def __str__(self):
        return f"{self.report} - {self.game.name}"

    def get_total_reaction_ms_avg(self):
        """
        평균 반응시간 계산 (밀리초)

        Returns:
            float or None: 평균 반응시간 (밀리초), 액션이 없으면 None
        """
        if self.total_play_actions_count == 0:
            return None
        return int(self.total_reaction_ms_sum / self.total_play_actions_count)

    def get_wrong_rate(self):
        """
        오답률 계산 (%)

        Returns:
            float or None: 오답률 (%), 액션이 없으면 None
        """
        if self.total_play_actions_count == 0:
            return None
        return round((self.total_wrong_count / self.total_play_actions_count) * 100, 1)

    def get_avg_rounds_count(self):
        """
        평균 도달 라운드 계산

        Returns:
            float or None: 평균 도달 라운드, 플레이가 없으면 None
        """
        if self.total_plays_count == 0:
            return None
        return round(self.total_play_rounds_count / self.total_plays_count, 1)

    def get_actual_latest_session_id(self):
        """
        해당 게임의 최신 세션 조회

        Returns:
            GameSession or None: 최신 세션 객체 또는 None
        """

        latest_result = (
            GameResult.objects.filter(
                child=self.report.child,
                game=self.game,
            )
            .select_related("session")
            .order_by("-updated_at")
            .first()
        )

        return latest_result.session.id if latest_result else None

    def get_max_rounds_ratio(self):
        """
        최대 라운드 도달 비율 계산 (%)

        Returns:
            float or None: 최대 라운드 도달 비율 (%), 플레이가 없으면 None
        """
        if self.total_plays_count == 0:
            return None
        return round((self.max_rounds_count / self.total_plays_count) * 100, 1)

    def is_up_to_date(self):
        """
        현재 게임 레포트가 최신 GameSession을 반영하고 있는지 확인

        Returns:
            bool: 최신 세션을 반영하고 있으면 True, 아니면 False
        """
        latest_session_id = self.get_actual_latest_session_id()

        if not latest_session_id:
            return False

        return self.last_reflected_session_id == latest_session_id

    def get_game_results(self):
        """
        해당 게임 레포트에 해당하는 모든 게임 결과 조회

        Returns:
            QuerySet: GameResult 쿼리셋
        """
        return GameResult.objects.filter(
            child=self.report.child,
            game=self.game,
        ).order_by("-created_at")

    def get_recent_trends(self, limit=3):
        """
        최근 N개의 GameResult 정보 반환

        Args:
            limit: 반환할 GameResult 개수 (기본값: 3)

        Returns:
            list: 최근 GameResult 정보 딕셔너리 리스트
        """
        recent_results = self.get_game_results()[:limit]
        trends = []

        for result in recent_results:
            trend_data = {
                "round_count": result.round_count,
                "success_count": result.success_count,
                "wrong_count": result.wrong_count,
            }

            # 반응시간은 게임 종류에 따라 선택적으로 추가
            if self.game.code == GameCodeChoice.KIDS_TRAFFIC:
                trend_data["reaction_ms_sum"] = result.reaction_ms_sum

            trends.append(trend_data)

        return trends

    def aggregate_statistics(self):
        """
        게임 결과를 집계하여 통계 컬럼들을 업데이트

        Returns:
            bool: 집계 성공 여부
        """
        game_results = self.get_game_results()

        if not game_results.exists():
            # 결과가 없으면 모든 통계를 0으로 초기화
            self.total_plays_count = 0
            self.total_play_rounds_count = 0
            self.max_rounds_count = 0
            self.total_reaction_ms_sum = 0
            self.total_play_actions_count = 0
            self.total_success_count = 0
            self.total_wrong_count = 0
            self.save(
                update_fields=[
                    "total_plays_count",
                    "total_play_rounds_count",
                    "max_rounds_count",
                    "total_reaction_ms_sum",
                    "total_play_actions_count",
                    "total_success_count",
                    "total_wrong_count",
                    "updated_at",
                ]
            )
            return False

        # 기본 통계 집계 (Django ORM 사용)
        stats = game_results.aggregate(
            total_plays=Count("id"),
            total_rounds=Sum("round_count"),
            total_reaction_ms=Sum("reaction_ms_sum"),
            total_success=Sum("success_count"),
            total_wrong=Sum("wrong_count"),
        )

        self.total_plays_count = stats["total_plays"] or 0
        self.total_play_rounds_count = stats["total_rounds"] or 0
        self.total_reaction_ms_sum = stats["total_reaction_ms"] or 0
        self.total_success_count = stats["total_success"] or 0
        self.total_wrong_count = stats["total_wrong"] or 0
        self.total_play_actions_count = self.total_success_count + self.total_wrong_count

        # 최대 도달 라운드 횟수 계산
        max_round = self.game.max_round
        self.max_rounds_count = game_results.filter(round_count=max_round).count()

        # 통계 컬럼들 저장
        self.save(
            update_fields=[
                "total_plays_count",
                "total_play_rounds_count",
                "max_rounds_count",
                "total_reaction_ms_sum",
                "total_play_actions_count",
                "total_success_count",
                "total_wrong_count",
                "updated_at",
            ]
        )

        return True
