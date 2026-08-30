"""
Base PDF Generator Service

URL을 받아 PDF를 생성하는 베이스 서비스 클래스입니다.
이 클래스를 상속하여 특정 URL, window size, PDF size 등을 지정한 서비스를 만들 수 있습니다.
"""

import time
from abc import ABC
from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from playwright.sync_api import sync_playwright

REPORT_WIDTH = settings.REPORT_WIDTH
REPORT_HEIGHT = settings.REPORT_HEIGHT


class BasePDFGenerator(ABC):
    """
    URL을 받아 PDF를 생성하는 베이스 클래스

    Usage:
        class MyPDFGenerator(BasePDFGenerator):
            def get_default_url(self):
                return "https://example.com"

            def get_viewport_size(self):
                return {"width": 1920, "height": 1080}

        generator = MyPDFGenerator()
        file_path, expiry_date = generator.generate_pdf(url="https://custom.com")
    """

    def get_default_url(self) -> Optional[str]:
        """
        기본 URL을 반환합니다.
        하위 클래스에서 오버라이드하여 사용합니다.
        """
        return None

    def get_viewport_size(self) -> dict:
        """
        브라우저 뷰포트 크기를 반환합니다.
        하위 클래스에서 오버라이드하여 커스터마이징할 수 있습니다.

        Returns:
            dict: {"width": int, "height": int}
        """
        return {"width": 1920, "height": 1080}

    def get_pdf_format(self) -> str:
        """
        PDF 페이지 포맷을 반환합니다.
        하위 클래스에서 오버라이드하여 커스터마이징할 수 있습니다.

        Returns:
            str: A4, Letter, Legal, Tabloid, Ledger, A0-A6 등
        """
        return "A4"

    def get_pdf_options(self) -> dict:
        """
        PDF 생성 옵션을 반환합니다.
        하위 클래스에서 오버라이드하여 추가 옵션을 설정할 수 있습니다.

        Returns:
            dict: playwright page.pdf()에 전달할 옵션들
        """
        return {
            "width": REPORT_WIDTH,
            "height": REPORT_HEIGHT,
            "print_background": True,
            "prefer_css_page_size": False,
        }

    def get_storage_path(self, filename: str) -> str:
        """
        PDF 파일이 저장될 경로를 반환합니다.
        하위 클래스에서 오버라이드하여 커스터마이징할 수 있습니다.

        Args:
            filename: 생성된 파일명

        Returns:
            str: storage에 저장될 경로
        """
        today = datetime.now().strftime("%Y/%m/%d")
        return f"pdfs/{today}/{filename}"

    def generate_filename(self) -> str:
        """
        고유한 PDF 파일명을 생성합니다.

        Returns:
            str: UUID 기반의 고유한 파일명
        """
        return f"{uuid4()}.pdf"

    def calculate_expiry_date(self) -> datetime:
        """
        PDF 파일의 만료 일시를 계산합니다.

        Returns:
            datetime: 만료 일시
        """
        expiry_days = getattr(settings, "PDF_EXPIRY_DAYS", 7)
        return datetime.now() + timedelta(days=expiry_days)

    def is_expired(self, created_at: datetime) -> bool:
        """
        PDF 파일이 만료되었는지 확인합니다.

        Args:
            created_at: 파일 생성 일시

        Returns:
            bool: 만료 여부
        """
        expiry_days = getattr(settings, "PDF_EXPIRY_DAYS", 7)
        expiry_date = created_at + timedelta(days=expiry_days)
        return datetime.now() > expiry_date

    def generate_pdf(self, url: Optional[str] = None, **kwargs) -> tuple[str, datetime]:
        """
        주어진 URL의 PDF를 생성하고 저장합니다.

        Args:
            url: PDF로 변환할 URL (None인 경우 get_default_url() 사용)
            **kwargs: 추가 옵션들 (viewport_size, pdf_options 등을 오버라이드)

        Returns:
            tuple[str, datetime]: (저장된 파일 경로, 만료 일시)

        Raises:
            ValueError: URL이 제공되지 않았고 기본 URL도 없는 경우
            Exception: PDF 생성 중 발생한 오류
        """
        # URL 결정
        target_url = url or self.get_default_url()
        if not target_url:
            raise ValueError("URL must be provided or get_default_url() must be implemented")

        # 옵션 설정
        viewport_size = kwargs.get("viewport_size", self.get_viewport_size())
        pdf_options = kwargs.get("pdf_options", self.get_pdf_options())

        # Playwright를 사용하여 PDF 생성
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(viewport=viewport_size)

                # 페이지 로드 및 대기
                page.goto(target_url, wait_until="networkidle")
                time.sleep(10)  # 추가 대기 시간 (필요시 조정)

                # PDF 생성
                pdf_bytes = page.pdf(**pdf_options)

                browser.close()

            # 파일 저장
            filename = self.generate_filename()
            storage_path = self.get_storage_path(filename)

            # ContentFile로 변환하여 storage에 저장
            content_file = ContentFile(pdf_bytes)
            saved_path = default_storage.save(storage_path, content_file)

            # 만료 일시 계산
            expiry_date = self.calculate_expiry_date()

            return saved_path, expiry_date

        except Exception as e:
            raise Exception(f"Failed to generate PDF from {target_url}: {e!s}") from e

    def get_pdf_url(self, file_path: str) -> str:
        """
        저장된 PDF 파일의 URL을 반환합니다.

        Args:
            file_path: storage에 저장된 파일 경로

        Returns:
            str: 파일 접근 URL
        """
        return default_storage.url(file_path)

    def delete_pdf(self, file_path: str) -> bool:
        """
        저장된 PDF 파일을 삭제합니다.

        Args:
            file_path: storage에 저장된 파일 경로

        Returns:
            bool: 삭제 성공 여부
        """
        try:
            if default_storage.exists(file_path):
                default_storage.delete(file_path)
                return True
            return False
        except Exception:
            return False
