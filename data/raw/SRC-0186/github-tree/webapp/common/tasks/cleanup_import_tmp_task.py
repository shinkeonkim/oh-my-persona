"""
import_export 임시 파일 정리 Celery task
"""

from datetime import timedelta

from django.core.files.storage import default_storage
from django.utils import timezone

from celery import shared_task

from common.utils.logger import get_logger

logger = get_logger(__name__)


@shared_task
def cleanup_import_tmp_files(hours=24):
  """
  import_export 임시 파일 정리

  Args:
      hours: 삭제할 파일의 최소 경과 시간 (기본값: 24시간)
  """
  storage_dir = "import_export_tmp"
  cutoff_time = timezone.now() - timedelta(hours=hours)

  logger.info(
    "import_export 임시 파일 정리 시작",
    hours=hours,
    cutoff_time=cutoff_time.isoformat(),
  )

  deleted_count = 0
  error_count = 0

  try:
    # storage_dir가 존재하는지 확인
    if not default_storage.exists(storage_dir):
      logger.info("임시 파일 디렉토리가 존재하지 않음", storage_dir=storage_dir)
      return f"디렉토리 없음: {storage_dir}"

    # storage_dir 내의 모든 파일 목록 가져오기
    dirs, files = default_storage.listdir(storage_dir)

    for filename in files:
      filepath = f"{storage_dir}/{filename}"

      try:
        # 파일의 수정 시간 확인
        modified_time = default_storage.get_modified_time(filepath)

        # timezone-aware datetime으로 변환
        if modified_time.tzinfo is None:
          modified_time = timezone.make_aware(modified_time)

        # cutoff_time보다 오래된 파일 삭제
        if modified_time < cutoff_time:
          default_storage.delete(filepath)
          deleted_count += 1
          logger.debug(
            "임시 파일 삭제",
            filepath=filepath,
            modified_time=modified_time.isoformat(),
          )

      except Exception as e:
        error_count += 1
        logger.warning(
          "임시 파일 처리 오류",
          filepath=filepath,
          error=str(e),
        )

    logger.info(
      "import_export 임시 파일 정리 완료",
      deleted_count=deleted_count,
      error_count=error_count,
    )

    return f"정리 완료: {deleted_count}개 삭제, {error_count}개 오류"

  except Exception as e:
    logger.error(
      "import_export 임시 파일 정리 실패",
      exception=e,
      exc_info=True,
    )
    raise
