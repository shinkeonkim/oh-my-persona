"""
레포트 생성 Celery Task

게임 레포트를 비동기로 생성하는 celery task입니다.
"""

import logging

from django.contrib.auth import get_user_model

from celery import shared_task
from reports.services import ReportGenerationService

from users.models import Child

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    name="reports.generate_report",
    max_retries=3,
    default_retry_delay=60,  # 1분
)
def generate_report_task(
    self,
    user_id: int,
    child_id: int,
) -> dict:
    """
    레포트를 비동기로 생성합니다.

    Args:
        user_id: 사용자 ID
        child_id: 아동 ID

    Returns:
        dict: {
            "success": bool,
            "message": str,
            "report_id": int,  # 성공 시 레포트 ID
        }

    Example:
        # Django shell에서 실행:
        from reports.tasks import generate_report_task
        result = generate_report_task.delay(
            user_id=1,
            child_id=2,
        )
        print(result.get())  # 결과 대기 및 출력
    """
    try:
        logger.info(f"Starting generate_report_task: user_id={user_id}, child_id={child_id}")

        User = get_user_model()

        # User와 Child 객체 조회
        user = User.objects.get(id=user_id)
        child = Child.objects.get(id=child_id)

        # 레포트 생성 실행
        report = ReportGenerationService.update_or_create_report(
            user=user,
            child=child,
        )

        logger.info(f"Report {report.id} generated successfully for user {user_id} and child {child_id}")

        return {
            "success": True,
            "message": "Report generated successfully",
            "report_id": report.id,
        }

    except Exception as exc:
        logger.error(f"Error in generate_report_task: {exc!s}", exc_info=True)

        # 재시도 로직
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying generate_report_task (attempt {self.request.retries + 1})")
            raise self.retry(exc=exc)

        # 최대 재시도 횟수 초과 시 실패 반환
        logger.error(f"Max retries exceeded for generate_report_task for user {user_id} and child {child_id}")
        return {
            "success": False,
            "message": f"Failed to generate report after {self.max_retries} retries: {exc!s}",
        }
