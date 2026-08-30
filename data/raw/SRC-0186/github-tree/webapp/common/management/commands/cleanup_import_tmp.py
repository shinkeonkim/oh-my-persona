"""
import_export 임시 파일 정리 명령어
"""

from datetime import datetime, timedelta

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from common.utils.logger import get_logger

logger = get_logger(__name__)


class Command(BaseCommand):
  help = "import_export 임시 파일 정리 (24시간 이상 된 파일 삭제)"

  def add_arguments(self, parser):
    parser.add_argument(
      "--hours",
      type=int,
      default=24,
      help="삭제할 파일의 최소 경과 시간 (기본값: 24시간)",
    )
    parser.add_argument(
      "--dry-run",
      action="store_true",
      help="실제로 삭제하지 않고 삭제될 파일만 표시",
    )

  def handle(self, *args, **options):
    hours = options["hours"]
    dry_run = options["dry_run"]

    storage_dir = "import_export_tmp"
    cutoff_time = datetime.now() - timedelta(hours=hours)

    self.stdout.write(f"임시 파일 정리 시작 (기준: {hours}시간 이전 파일)")
    self.stdout.write(f"Cutoff time: {cutoff_time}")

    deleted_count = 0
    error_count = 0

    try:
      # storage_dir 내의 모든 파일 목록 가져오기
      dirs, files = default_storage.listdir(storage_dir)

      for filename in files:
        filepath = f"{storage_dir}/{filename}"

        try:
          # 파일의 수정 시간 확인
          modified_time = default_storage.get_modified_time(filepath)

          # timezone-aware datetime으로 변환 (필요시)
          if modified_time.tzinfo is None:
            from django.utils import timezone

            modified_time = timezone.make_aware(modified_time)

          # cutoff_time과 비교 (timezone-aware로 변환)
          from django.utils import timezone

          cutoff_aware = timezone.make_aware(cutoff_time) if cutoff_time.tzinfo is None else cutoff_time

          if modified_time < cutoff_aware:
            if dry_run:
              self.stdout.write(f"[DRY-RUN] 삭제 예정: {filepath} (수정 시간: {modified_time})")
            else:
              default_storage.delete(filepath)
              self.stdout.write(f"삭제 완료: {filepath}")

            deleted_count += 1

        except Exception as e:
          self.stderr.write(f"파일 처리 오류: {filepath} - {str(e)}")
          error_count += 1

      if dry_run:
        self.stdout.write(self.style.SUCCESS(f"\n[DRY-RUN] 총 {deleted_count}개 파일이 삭제 예정입니다."))
      else:
        self.stdout.write(self.style.SUCCESS(f"\n총 {deleted_count}개 파일을 삭제했습니다."))

      if error_count > 0:
        self.stdout.write(self.style.WARNING(f"오류 발생: {error_count}개 파일"))

      logger.info(
        "import_export 임시 파일 정리 완료",
        deleted_count=deleted_count,
        error_count=error_count,
        dry_run=dry_run,
        hours=hours,
      )

    except Exception as e:
      self.stderr.write(self.style.ERROR(f"디렉토리 접근 오류: {str(e)}"))
      logger.error("import_export 임시 파일 정리 실패", exception=e, exc_info=True)
