import logging

from django.db import transaction

from games.models import Game
from reports.choices import ReportStatusChoice
from reports.models import Report

from .game_report_generation_service import GameReportGenerationService
from .report_concentration_score_generation_service import ReportConcentrationScoreGenerationService

logger = logging.getLogger(__name__)


class ReportGenerationService:
    """
    레포트 생성 및 업데이트 서비스
    """

    @staticmethod
    @transaction.atomic
    def update_or_create_report(user, child):
        """
        사용자와 아동에 대한 레포트 조회 또는 생성

        Args:
            user: 사용자 객체
            child: 아동 객체

        Returns:
            Report 객체
        """
        report, _created = Report.objects.get_or_create_for_user_child(user=user, child=child)

        games = Game.objects.active()

        for game in games:
            GameReportGenerationService.update_or_create_game_report(report, game)

        # 집중력 점수 계산 및 업데이트
        ReportConcentrationScoreGenerationService.update_concentration_score(report)

        # 레포트 생성 완료 후 COMPLETED 상태로 변경
        report.status = ReportStatusChoice.COMPLETED
        report.save(update_fields=["status", "updated_at"])

        logger.info(f"Report {report.id} status updated to COMPLETED")

        return report
