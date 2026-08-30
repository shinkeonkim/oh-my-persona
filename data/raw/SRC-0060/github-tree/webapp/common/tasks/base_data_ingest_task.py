"""
Base Task for Celery data ingestion tasks with Slack notification support
"""

import logging
import traceback
from typing import Any, Optional

from django.conf import settings

from celery import Task

from common.utils.slack import SlackUtil

logger = logging.getLogger(__name__)

IS_SLACK_ENABLED = settings.ENVIRONMENT == "production"


class BaseDataIngestTask(Task):
  """Base Celery Task for data ingestion with Slack notification

  데이터 수집 task의 base 클래스입니다.
  모든 task의 실행 결과를 Slack으로 전송합니다.

  Usage:
    class MyTask(BaseDataIngestTask):
      name = "companies.tasks.my_task"

      def run(self, *args, **kwargs):
        return {"status": "success", "count": 10}

    my_task = shared_task(base=MyTask, bind=True)
  """

  def on_success(self, retval: Any, task_id: str, args: tuple, kwargs: dict) -> None:
    """Task 성공 시 호출되는 콜백

    Args:
      retval: Task의 반환값
      task_id: Task ID
      args: Task 위치 인자
      kwargs: Task 키워드 인자
    """
    task_name = self.name

    logger.info(f"Task {task_name} ({task_id}) succeeded with result: {retval}")

    if not IS_SLACK_ENABLED:
      return
    # Slack 알림 전송
    self._send_slack_notification(
      task_name=task_name,
      task_id=task_id,
      status="success",
      result=retval,
      args=args,
      kwargs=kwargs,
    )

  def on_failure(
    self,
    exc: Exception,
    task_id: str,
    args: tuple,
    kwargs: dict,
    einfo: Any,
  ) -> None:
    """Task 실패 시 호출되는 콜백

    Args:
      exc: 발생한 예외
      task_id: Task ID
      args: Task 위치 인자
      kwargs: Task 키워드 인자
      einfo: Exception info
    """
    task_name = self.name

    logger.error(f"Task {task_name} ({task_id}) failed: {exc}", exc_info=einfo)

    if not IS_SLACK_ENABLED:
      return

    # Slack 알림 전송
    self._send_slack_notification(
      task_name=task_name,
      task_id=task_id,
      status="failure",
      error=str(exc),
      error_traceback=traceback.format_exc(),
      args=args,
      kwargs=kwargs,
    )

  def _send_slack_notification(
    self,
    task_name: str,
    task_id: str,
    status: str,
    result: Optional[Any] = None,
    error: Optional[str] = None,
    error_traceback: Optional[str] = None,
    args: Optional[tuple] = None,
    kwargs: Optional[dict] = None,
  ) -> None:
    """Slack 알림 전송

    Args:
      task_name: Task 이름
      task_id: Task ID
      status: 'success' 또는 'failure'
      result: Task 성공 시 결과값
      error: Task 실패 시 에러 메시지
      error_traceback: Task 실패 시 traceback
      args: Task 위치 인자
      kwargs: Task 키워드 인자
    """
    try:
      # 상태 이모지
      status_emoji = ":white_check_mark:" if status == "success" else ":x:"

      # Header 생성
      blocks = [
        SlackUtil.create_slack_header_block(f"{status_emoji} {task_name} - {status.upper()}"),
        SlackUtil.create_slack_section_block(f"*Task Name:* `{task_name}`\n*Task ID:* `{task_id}`"),
        SlackUtil.create_slack_divider_block(),
      ]

      # 성공 시 결과 정보 추가
      if status == "success" and result:
        result_text = self._format_result(result)
        blocks.append(SlackUtil.create_slack_section_block(f"*결과:*\n{result_text}"))

      # 실패 시 에러 정보 추가
      if status == "failure" and error:
        blocks.append(SlackUtil.create_slack_section_block(f"*Error:*\n```{error}```"))

        # Traceback은 스레드로 전송 (너무 길 수 있음)
        if error_traceback:
          blocks.append(SlackUtil.create_slack_section_block("*Traceback:* (스레드 참조)"))

      # Task 인자 정보 추가 (있는 경우)
      if args or kwargs:
        args_text = self._format_args(args, kwargs)
        if args_text:
          blocks.append(SlackUtil.create_slack_divider_block())
          blocks.append(SlackUtil.create_slack_section_block(f"*Arguments:*\n{args_text}"))

      # Slack 메시지 전송
      fallback_text = f"Task {task_name} {status}: {result or error}"
      SlackUtil.send_slack_plain_message(
        blocks=blocks,
        fallback_text=fallback_text,
        category="data_collect",
      )

      # Traceback을 스레드로 전송 (TODO: 스레드 지원 추가 필요)
      # if error_traceback:
      #   self._send_traceback_to_thread(task_id, error_traceback)

    except Exception as e:
      logger.error(f"Slack 알림 전송 실패: {e}", exc_info=True)

  def _format_result(self, result: Any) -> str:
    """Task 결과를 포맷팅

    Args:
      result: Task 결과값

    Returns:
      str: 포맷팅된 결과 문자열
    """
    if isinstance(result, dict):
      lines = []
      for key, value in result.items():
        # 통계 정보를 보기 좋게 포맷팅
        if isinstance(value, (int, float)):
          lines.append(f"• *{key}:* {value:,}")
        else:
          lines.append(f"• *{key}:* {value}")
      return "\n".join(lines)
    else:
      return str(result)

  def _format_args(self, args: Optional[tuple], kwargs: Optional[dict]) -> str:
    """Task 인자를 포맷팅

    Args:
      args: 위치 인자
      kwargs: 키워드 인자

    Returns:
      str: 포맷팅된 인자 문자열
    """
    lines = []

    if args:
      for i, arg in enumerate(args):
        lines.append(f"• arg{i}: `{arg}`")

    if kwargs:
      for key, value in kwargs.items():
        lines.append(f"• {key}: `{value}`")

    return "\n".join(lines) if lines else ""
