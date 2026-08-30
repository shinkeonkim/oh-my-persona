import logging

from django.db.models import Avg, Case, F, FloatField, When
from django.db.models.functions import Cast

from games.choices import GameCodeChoice
from reports.models import GameReport, Report

logger = logging.getLogger(__name__)

# 최근 게임 결과를 고려할 개수 (최근 2개 vs 나머지 전체)
RECENT_GAMES_COUNT = 2

# 게임별 최대 총 액션 수 (전체 라운드 완벽 플레이 시)
GAME_MAX_TOTAL_ACTIONS = {
    GameCodeChoice.KIDS_TRAFFIC: 50,  # 10라운드 * 5액션/라운드
    GameCodeChoice.BB_STAR: 69,  # 3 4 5 6 7 8 9 9 9 9
}

# 점수 계산 가중치 (총 110%, 100점 초과 시 커팅)
WEIGHT_SUCCESS_RATE = 0.4  # 성공률 가중치 (40%)
WEIGHT_MAX_ROUND_ACHIEVEMENT = 0.3  # 최대 라운드 도달 가중치 (30%)
WEIGHT_CONSISTENCY = 0.3  # 일관성 가중치 (30%)
WEIGHT_RECENT_IMPROVEMENT = 0.1  # 최근 개선도 가중치 (10%) - 보너스 점수


class ReportConcentrationScoreGenerationService:
    """
    레포트 집중력 점수 생성 서비스

    점수는 0-100점 사이이며, 다음 요소를 고려합니다:
    1. 전체 성공률 (40%)
    2. 최대 라운드 도달률 (30%)
    3. 플레이 일관성 (30%)
    4. 최근 개선도 (10%) - 보너스 점수
    총 110% 구성, 100점 초과 시 100점으로 커팅
    """

    @staticmethod
    def calculate_concentration_score(report: Report) -> int:
        """
        레포트의 집중력 점수 계산

        Args:
            report: Report 객체

        Returns:
            int: 0-100 사이의 집중력 점수
        """
        game_reports = GameReport.objects.by_report(report).select_related("game")

        if not game_reports.exists():
            logger.info(f"No game reports found for report {report.id}. Returning score 0.")
            return 0

        total_score = 0.0
        game_count = 0

        for game_report in game_reports:
            if game_report.total_plays_count == 0:
                continue

            game_score = ReportConcentrationScoreGenerationService._calculate_game_score(game_report)
            total_score += game_score
            game_count += 1

        if game_count == 0:
            return 0

        # 평균 점수 계산
        average_score = total_score / game_count

        # 0-100 범위로 제한 (110% 구성이므로 100 초과 가능, 커팅 필요)
        final_score = max(0, min(100, int(round(average_score))))

        logger.info(f"Calculated concentration score for report {report.id}: {final_score}")

        return final_score

    @staticmethod
    def _calculate_game_score(game_report: GameReport) -> float:
        """
        개별 게임의 집중력 점수 계산

        Args:
            game_report: GameReport 객체

        Returns:
            float: 0-110 사이의 점수 (100 초과 가능)
        """
        # 1. 성공률 점수 (40%)
        success_rate_score = ReportConcentrationScoreGenerationService._calculate_success_rate_score(game_report)

        # 2. 최대 라운드 도달 점수 (30%)
        max_round_score = ReportConcentrationScoreGenerationService._calculate_max_round_score(game_report)

        # 3. 일관성 점수 (30%)
        consistency_score = ReportConcentrationScoreGenerationService._calculate_consistency_score(game_report)

        # 4. 최근 개선도 점수 (10%) - 보너스
        improvement_score = ReportConcentrationScoreGenerationService._calculate_improvement_score(game_report)

        # 가중치 적용 (총 110% 가능)
        total_score = (
            success_rate_score * WEIGHT_SUCCESS_RATE
            + max_round_score * WEIGHT_MAX_ROUND_ACHIEVEMENT
            + consistency_score * WEIGHT_CONSISTENCY
            + improvement_score * WEIGHT_RECENT_IMPROVEMENT
        )

        logger.debug(
            f"Game {game_report.game.code} scores - "
            f"Success: {success_rate_score:.1f}, "
            f"MaxRound: {max_round_score:.1f}, "
            f"Consistency: {consistency_score:.1f}, "
            f"Improvement: {improvement_score:.1f}, "
            f"Total: {total_score:.1f}"
        )

        return total_score

    @staticmethod
    def _calculate_success_rate_score(game_report: GameReport) -> float:
        """
        성공률 기반 점수 계산

        Args:
            game_report: GameReport 객체

        Returns:
            float: 0-100 사이의 점수
        """
        if game_report.total_play_actions_count == 0:
            return 0.0

        success_rate = (game_report.total_success_count / game_report.total_play_actions_count) * 100

        # 성공률을 그대로 점수로 사용
        return min(100.0, success_rate)

    @staticmethod
    def _calculate_max_round_score(game_report: GameReport) -> float:
        """
        최대 라운드 도달률 기반 점수 계산

        Args:
            game_report: GameReport 객체

        Returns:
            float: 0-100 사이의 점수
        """
        if game_report.total_plays_count == 0:
            return 0.0

        # 최대 라운드 도달 비율
        max_round_achievement_rate = (game_report.max_rounds_count / game_report.total_plays_count) * 100

        # 평균 도달 라운드 비율
        avg_rounds_count = game_report.get_avg_rounds_count()
        if avg_rounds_count is None:
            avg_round_rate = 0.0
        else:
            avg_round_rate = (avg_rounds_count / game_report.game.max_round) * 100

        # 두 지표의 평균 사용 (최대 도달률 60%, 평균 도달률 40%)
        score = max_round_achievement_rate * 0.6 + avg_round_rate * 0.4

        return min(100.0, score)

    @staticmethod
    def _calculate_consistency_score(game_report: GameReport) -> float:
        """
        플레이 일관성 점수 계산 (오답률의 역수 기반)

        Args:
            game_report: GameReport 객체

        Returns:
            float: 0-100 사이의 점수
        """
        wrong_rate = game_report.get_wrong_rate()

        if wrong_rate is None:
            return 0.0

        # 오답률이 낮을수록 높은 점수
        # 오답률 0% = 100점, 오답률 100% = 0점
        consistency_score = 100.0 - wrong_rate

        return max(0.0, consistency_score)

    @staticmethod
    def _calculate_improvement_score(game_report: GameReport) -> float:
        """
        최근 게임 결과의 개선도 점수 계산 (보너스 점수)

        최근 2개 게임의 평균 성공률과 나머지 전체 게임의 평균 성공률을 비교

        Args:
            game_report: GameReport 객체

        Returns:
            float: 0-100 사이의 점수
        """

        all_results_queryset = game_report.get_game_results()
        total_count = all_results_queryset.count()

        if total_count < 2:
            # 비교할 데이터가 부족하면 기본 점수 반환 (50점)
            return 50.0

        # ORM을 사용하여 성공률 계산
        # success_rate = success_count / (success_count + wrong_count) * 100
        results_with_rate = all_results_queryset.annotate(
            total_actions=F("success_count") + F("wrong_count"),
            success_rate=Case(
                When(
                    total_actions__gt=0,
                    then=Cast(F("success_count"), FloatField()) / Cast(F("total_actions"), FloatField()) * 100,
                ),
                default=0.0,
                output_field=FloatField(),
            ),
        ).filter(total_actions__gt=0)

        valid_count = results_with_rate.count()

        if valid_count < 2:
            return 50.0

        # 최근 2개 게임의 평균 성공률
        recent_results = results_with_rate[:RECENT_GAMES_COUNT]
        recent_avg = recent_results.aggregate(avg_rate=Avg("success_rate"))["avg_rate"] or 0.0

        # 나머지 전체 게임의 평균 성공률
        if valid_count > RECENT_GAMES_COUNT:
            older_results = results_with_rate[RECENT_GAMES_COUNT:]
            older_avg = older_results.aggregate(avg_rate=Avg("success_rate"))["avg_rate"] or 0.0
        else:
            # 나머지가 없으면 최근 평균과 동일하게 설정 (개선도 0)
            older_avg = recent_avg

        # 개선도 계산 (-100 ~ +100)
        improvement = recent_avg - older_avg

        # 0-100 스케일로 변환
        # 개선도가 +20% 이상이면 100점
        # 개선도가 0%이면 50점
        # 개선도가 -20% 이하이면 0점
        improvement_score = 50 + (improvement * 2.5)

        return max(0.0, min(100.0, improvement_score))

    @staticmethod
    def update_concentration_score(report: Report) -> Report:
        """
        레포트의 집중력 점수를 계산하여 업데이트

        Args:
            report: Report 객체

        Returns:
            Report: 업데이트된 Report 객체
        """
        concentration_score = ReportConcentrationScoreGenerationService.calculate_concentration_score(report)

        report.concentration_score = concentration_score
        report.save(update_fields=["concentration_score", "updated_at"])

        logger.info(f"Updated concentration score for report {report.id}: {concentration_score}")

        return report
