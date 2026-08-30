from typing import Optional

from django.core.files.storage import default_storage

from .base_email_service import BaseEmailService


class FileAttachmentEmailService(BaseEmailService):
    """
    파일 첨부 기능이 포함된 이메일 서비스 베이스 클래스

    storage에 저장된 파일을 첨부하여 이메일을 전송합니다.
    """

    def attach_file_from_storage(
        self, file_path: str, filename: Optional[str] = None, mimetype: str = "application/octet-stream"
    ) -> tuple[str, bytes, str]:
        """
        storage에 저장된 파일을 첨부 파일로 변환합니다.

        Args:
            file_path: storage에 저장된 파일 경로
            filename: 첨부 파일명 (None이면 원본 파일명 사용)
            mimetype: MIME 타입

        Returns:
            tuple[str, bytes, str]: (파일명, 파일 내용, MIME 타입)

        Raises:
            FileNotFoundError: 파일이 존재하지 않는 경우
        """
        if not default_storage.exists(file_path):
            raise FileNotFoundError(f"File not found in storage: {file_path}")

        # 파일 내용 읽기
        with default_storage.open(file_path, "rb") as f:
            content = f.read()

        # 파일명 결정
        if not filename:
            # file_path에서 파일명 추출
            filename = file_path.split("/")[-1]

        return filename, content, mimetype
