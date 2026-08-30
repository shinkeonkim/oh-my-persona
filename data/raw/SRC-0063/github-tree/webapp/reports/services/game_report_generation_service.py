import logging

from django.db import transaction

from games.choices import GameCodeChoice
from reports.llm.generator import (
    BBStarGameReportAdviceGenerator,
    KidsTrafficGameReportAdviceGenerator,
)
from reports.models import GameReport, GameReportAdvice

logger = logging.getLogger(__name__)


class GameReportGenerationService:
    """
    게임 레포트 생성 및 업데이트 서비스
    """

    @staticmethod
    def update_or_create_game_report(report, game):
        """
        특정 게임에 대한 GameReport 업데이트 또는 생성

        Args:
            report: Report 객체
            game: Game 객체

        Returns:
            GameReport 객체
        """
        game_report = GameReportGenerationService._update_game_report_statistics(report, game)

        if game_report and game_report.total_plays_count > 0:
            GameReportGenerationService._generate_game_report_advice(game_report, game)

        return game_report

    @staticmethod
    @transaction.atomic
    def _update_game_report_statistics(report, game):
        """
        GameReport의 통계 데이터를 집계하고 저장

        Args:
            report: Report 객체
            game: Game 객체

        Returns:
            GameReport 객체 또는 None (업데이트가 필요 없는 경우)
        """
        # GameReport 조회 또는 생성
        game_report, created = GameReport.objects.get_or_create_for_report_and_game(
            report=report,
            game=game,
        )

        # 최신 세션 확인
        latest_session_id = game_report.get_actual_latest_session_id()

        # 이미 최신 상태라면 업데이트 불필요
        if not created and game_report.last_reflected_session_id == latest_session_id:
            return game_report

        # 게임 관련 통계 집계 및 저장
        game_report.aggregate_statistics()

        # 통계 컬럼을 재로드하여 최신 데이터 가져오기
        game_report.refresh_from_db(
            fields=[
                "total_plays_count",
                "total_play_rounds_count",
                "max_rounds_count",
                "total_reaction_ms_sum",
                "total_play_actions_count",
                "total_success_count",
                "total_wrong_count",
            ]
        )

        # 최신 세션으로 업데이트
        game_report.last_reflected_session_id = latest_session_id
        game_report.save(update_fields=["last_reflected_session_id", "updated_at"])

        return game_report

    @staticmethod
    def _generate_game_report_advice(game_report, game):
        """
        LLM을 사용하여 게임 레포트 조언 생성

        Args:
            game_report: GameReport 객체 (통계 컬럼들에 데이터 포함)
            game: Game 객체
        """
        # 기존 조언 삭제
        GameReportAdvice.objects.filter(game_report=game_report).delete()

        # 통계 데이터가 없으면 조언 생성 건너뛰기
        if game_report.total_plays_count == 0:
            logger.info(f"No data available for game report {game_report.id}. Skipping advice generation.")
            return

        # 통계 데이터 준비
        total_reaction_ms_avg = game_report.get_total_reaction_ms_avg()
        wrong_rate = game_report.get_wrong_rate()
        avg_rounds_count = game_report.get_avg_rounds_count()

        statistics = {
            "total_plays_count": game_report.total_plays_count,
            "total_play_rounds_count": game_report.total_play_rounds_count,
            "max_rounds_count": game_report.max_rounds_count,
            "max_rounds_ratio": (
                game_report.get_max_rounds_ratio() if game_report.get_max_rounds_ratio() is not None else 0
            ),
            "avg_rounds_count": avg_rounds_count if avg_rounds_count is not None else 0,
            "total_reaction_ms_avg": total_reaction_ms_avg if total_reaction_ms_avg is not None else 0,
            "total_play_actions_count": game_report.total_play_actions_count,
            "total_success_count": game_report.total_success_count,
            "total_wrong_count": game_report.total_wrong_count,
            "wrong_rate": wrong_rate if wrong_rate is not None else 0,
            "recent_trends": game_report.get_recent_trends(),
        }

        # 게임별로 적절한 Generator 선택
        generator = None

        if game.code == GameCodeChoice.KIDS_TRAFFIC:
            generator = KidsTrafficGameReportAdviceGenerator()
        elif game.code == GameCodeChoice.BB_STAR:
            generator = BBStarGameReportAdviceGenerator()
        else:
            logger.warning(f"Unknown game code: {game.code}. Skipping advice generation.")
            return

        # LLM을 사용하여 조언 생성
        try:
            advice_list = generator.generate_advice(statistics)

            # 조언을 DB에 저장
            for advice_item in advice_list:
                GameReportAdvice.objects.create(
                    game_report=game_report,
                    game=game,
                    title=advice_item["title"],
                    description=advice_item["description"],
                )

            logger.info(f"Successfully generated {len(advice_list)} advices for game report {game_report.id}")

        except Exception as e:
            # 오류 발생 시 에러 메시지와 함께 조언 저장
            logger.error(f"Failed to generate advice for game report {game_report.id}: {str(e)}")
            GameReportAdvice.objects.create(
                game_report=game_report,
                game=game,
                title="조언 생성 실패",
                description="조언 생성 중 오류가 발생했습니다.",
                error_message=str(e),
            )
