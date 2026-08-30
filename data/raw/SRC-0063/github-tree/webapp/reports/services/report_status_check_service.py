import logging

from django.db import transaction

from games.models import Game, GameResult
from reports.choices import ReportStatusChoice
from reports.models import Report
from reports.tasks.report_task import generate_report_task

logger = logging.getLogger(__name__)


class ReportStatusCheckService:
    def __init__(self, report):
        self.report = report
        self.child = report.child

        self.played_game_ids = self._played_game_ids()  # 플레이한 게임 ID 목록
        self.unplayed_game_ids = self._unplayed_game_ids()  # 플레이하지 않은 게임 ID 목록
        self.outdated_result_game_ids = self._outdated_result_game_ids()  # 최신 세션이 반영되지 않은 게임 ID 목록

    @transaction.atomic
    def check_status(self):
        locked_report = Report.objects.select_for_update().get(id=self.report.id)

        if locked_report.status == ReportStatusChoice.GENERATING:
            return  # 이미 처리 진행 중인 경우, 상태 변경이 더이상 일어나지 않도록 함

        if not self._is_all_played():
            locked_report.status = ReportStatusChoice.NO_GAMES_PLAYED
            locked_report.save(
                update_fields=["status"],
            )
            return

        if self._is_all_up_to_date():
            locked_report.status = ReportStatusChoice.COMPLETED
            locked_report.save(
                update_fields=["status"],
            )
            return

        # 레포트 생성 작업 트리거
        try:
            # GENERATING 상태로 변경
            locked_report.status = ReportStatusChoice.GENERATING
            locked_report.save(update_fields=["status"])

            # Celery task를 통해 비동기로 레포트 생성 실행
            generate_report_task.delay(
                user_id=locked_report.user.id,
                child_id=self.child.id,
            )

            logger.info(f"Report {locked_report.id} generation task triggered")

        except Exception as e:
            # 오류 발생 시 ERROR 상태로 변경
            logger.error(f"Failed to trigger report generation for {locked_report.id}: {str(e)}")
            locked_report.refresh_from_db()
            locked_report.status = ReportStatusChoice.ERROR
            locked_report.save(update_fields=["status"])

    def _is_all_played(self):
        """모든 활성화된 게임을 플레이했는지 여부 확인"""
        return len(self.unplayed_game_ids) == 0

    def _is_all_up_to_date(self):
        """모든 게임 결과가 최신 세션을 반영하고 있는지 여부 확인"""
        return len(self.outdated_result_game_ids) == 0

    def _all_game_ids(self):
        """모든 활성화된 게임 ID 조회"""
        return Game.objects.active().values_list("id", flat=True)

    def _played_game_ids(self):
        """이 아동이 플레이한 게임 ID 목록 조회"""
        games = GameResult.objects.filter(child=self.child)
        return games.values_list("game_id", flat=True).distinct()

    def _played_games(self):
        """이 아동이 플레이한 게임 목록 조회"""
        return Game.objects.filter(id__in=self.played_game_ids)

    def _unplayed_game_ids(self):
        """플레이하지 않은 게임 ID 목록 조회"""
        all_game_ids = set(self._all_game_ids())
        played_game_ids = set(self.played_game_ids)
        return list(all_game_ids - played_game_ids)

    def _unplayed_games(self):
        """플레이하지 않은 게임 목록 조회"""
        return Game.objects.filter(id__in=self.unplayed_game_ids)

    def _outdated_result_game_ids(self):
        """최신 세션이 반영되지 않은 게임 ID 목록 조회"""
        game_report = self.report.game_reports.all().select_related("game")
        outdated_game_ids = list(self._all_game_ids())

        for gr in game_report:
            latest_session_id = gr.get_actual_latest_session_id()
            if gr.last_reflected_session_id == latest_session_id:
                outdated_game_ids.remove(gr.game.id)

        return outdated_game_ids
