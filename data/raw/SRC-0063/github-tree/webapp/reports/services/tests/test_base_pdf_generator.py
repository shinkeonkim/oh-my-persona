from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from django.test import TestCase, override_settings

import pytest
from reports.services.base_pdf_generator import BasePDFGenerator


@pytest.mark.django_db
class BasePDFGeneratorTests(TestCase):
    """BasePDFGenerator 테스트"""

    def setUp(self):
        """테스트 설정"""
        self.generator = BasePDFGenerator()

    def test_get_default_url(self):
        """기본 URL 반환 테스트"""
        url = self.generator.get_default_url()
        self.assertIsNone(url)  # BasePDFGenerator는 None 반환

    def test_get_viewport_size(self):
        """뷰포트 크기 반환 테스트"""
        viewport = self.generator.get_viewport_size()
        self.assertEqual(viewport["width"], 1920)
        self.assertEqual(viewport["height"], 1080)

    def test_get_pdf_format(self):
        """PDF 포맷 반환 테스트"""
        pdf_format = self.generator.get_pdf_format()
        self.assertEqual(pdf_format, "A4")

    def test_get_storage_path(self):
        """저장 경로 생성 테스트"""
        filename = "test.pdf"
        path = self.generator.get_storage_path(filename)

        # pdfs/YYYY/MM/DD/test.pdf 형식
        self.assertIn("pdfs/", path)
        self.assertIn(filename, path)

    def test_generate_filename(self):
        """파일명 생성 테스트"""
        filename = self.generator.generate_filename()

        self.assertTrue(filename.endswith(".pdf"))
        # UUID 형식인지 확인 (최소 길이)
        self.assertGreater(len(filename), 30)

    @override_settings(PDF_EXPIRY_DAYS=7)
    def test_calculate_expiry_date(self):
        """만료 일시 계산 테스트"""
        now = datetime.now()
        expiry_date = self.generator.calculate_expiry_date()

        # 7일 후
        expected_date = now + timedelta(days=7)
        time_diff = abs((expiry_date - expected_date).total_seconds())

        # 1분 이내 오차 허용
        self.assertLess(time_diff, 60)

    @override_settings(PDF_EXPIRY_DAYS=7)
    def test_is_expired_not_expired(self):
        """만료되지 않은 파일 테스트"""
        created_at = datetime.now() - timedelta(days=3)  # 3일 전
        is_expired = self.generator.is_expired(created_at)

        self.assertFalse(is_expired)

    @override_settings(PDF_EXPIRY_DAYS=7)
    def test_is_expired_expired(self):
        """만료된 파일 테스트"""
        created_at = datetime.now() - timedelta(days=10)  # 10일 전
        is_expired = self.generator.is_expired(created_at)

        self.assertTrue(is_expired)

    @patch("reports.services.base_pdf_generator.sync_playwright")
    @patch("reports.services.base_pdf_generator.default_storage")
    def test_generate_pdf_success(self, mock_storage, mock_playwright):
        """PDF 생성 성공 테스트 (Playwright 모킹)"""
        # Mock Playwright
        mock_page = Mock()
        mock_page.pdf.return_value = b"fake_pdf_content"

        mock_browser = Mock()
        mock_browser.new_page.return_value = mock_page

        mock_p = Mock()
        mock_p.chromium.launch.return_value = mock_browser

        mock_playwright.return_value.__enter__.return_value = mock_p

        # Mock storage
        mock_storage.save.return_value = "pdfs/2024/11/11/test.pdf"

        # 실행
        url = "https://example.com/test"
        file_path, expiry_date = self.generator.generate_pdf(url=url)

        # 검증
        self.assertEqual(file_path, "pdfs/2024/11/11/test.pdf")
        self.assertIsInstance(expiry_date, datetime)

        # Playwright 호출 확인
        mock_page.goto.assert_called_once_with(url, wait_until="networkidle")
        mock_page.pdf.assert_called_once()
        mock_browser.close.assert_called_once()

        # Storage 저장 확인
        mock_storage.save.assert_called_once()

    def test_generate_pdf_without_url_raises_error(self):
        """URL 없이 PDF 생성 시도 시 오류 발생 테스트"""
        with self.assertRaises(ValueError) as context:
            self.generator.generate_pdf()

        self.assertIn("URL must be provided", str(context.exception))

    @patch("reports.services.base_pdf_generator.sync_playwright")
    def test_generate_pdf_playwright_error(self, mock_playwright):
        """Playwright 오류 발생 테스트"""
        # Mock Playwright - 예외 발생
        mock_playwright.return_value.__enter__.side_effect = Exception("Playwright launch failed")

        # 실행 및 검증
        with self.assertRaises(Exception) as context:
            self.generator.generate_pdf(url="https://example.com")

        self.assertIn("Failed to generate PDF", str(context.exception))

    @patch("reports.services.base_pdf_generator.default_storage")
    def test_get_pdf_url(self, mock_storage):
        """PDF URL 조회 테스트"""
        mock_storage.url.return_value = "https://storage.example.com/pdfs/test.pdf"

        url = self.generator.get_pdf_url("pdfs/test.pdf")

        self.assertEqual(url, "https://storage.example.com/pdfs/test.pdf")
        mock_storage.url.assert_called_once_with("pdfs/test.pdf")

    @patch("reports.services.base_pdf_generator.default_storage")
    def test_delete_pdf_success(self, mock_storage):
        """PDF 삭제 성공 테스트"""
        mock_storage.exists.return_value = True

        result = self.generator.delete_pdf("pdfs/test.pdf")

        self.assertTrue(result)
        mock_storage.delete.assert_called_once_with("pdfs/test.pdf")

    @patch("reports.services.base_pdf_generator.default_storage")
    def test_delete_pdf_file_not_exists(self, mock_storage):
        """존재하지 않는 파일 삭제 시도 테스트"""
        mock_storage.exists.return_value = False

        result = self.generator.delete_pdf("pdfs/nonexistent.pdf")

        self.assertFalse(result)
        mock_storage.delete.assert_not_called()

    @patch("reports.services.base_pdf_generator.default_storage")
    def test_delete_pdf_error(self, mock_storage):
        """삭제 중 오류 발생 테스트"""
        mock_storage.exists.return_value = True
        mock_storage.delete.side_effect = Exception("Delete failed")

        result = self.generator.delete_pdf("pdfs/test.pdf")

        self.assertFalse(result)

    @patch("reports.services.base_pdf_generator.sync_playwright")
    @patch("reports.services.base_pdf_generator.default_storage")
    def test_generate_pdf_with_custom_viewport(self, mock_storage, mock_playwright):
        """커스텀 뷰포트로 PDF 생성 테스트"""
        # Mock Playwright
        mock_page = Mock()
        mock_page.pdf.return_value = b"fake_pdf_content"

        mock_browser = Mock()
        mock_browser.new_page.return_value = mock_page

        mock_p = Mock()
        mock_p.chromium.launch.return_value = mock_browser

        mock_playwright.return_value.__enter__.return_value = mock_p

        # Mock storage
        mock_storage.save.return_value = "pdfs/test.pdf"

        # 커스텀 뷰포트
        custom_viewport = {"width": 1280, "height": 720}

        # 실행
        file_path, expiry_date = self.generator.generate_pdf(
            url="https://example.com",
            viewport_size=custom_viewport,
        )

        # 검증 - 커스텀 뷰포트로 페이지 생성
        mock_browser.new_page.assert_called_once_with(viewport=custom_viewport)

    @patch("reports.services.base_pdf_generator.sync_playwright")
    @patch("reports.services.base_pdf_generator.default_storage")
    def test_generate_pdf_with_custom_options(self, mock_storage, mock_playwright):
        """커스텀 PDF 옵션으로 생성 테스트"""
        # Mock Playwright
        mock_page = Mock()
        mock_page.pdf.return_value = b"fake_pdf_content"

        mock_browser = Mock()
        mock_browser.new_page.return_value = mock_page

        mock_p = Mock()
        mock_p.chromium.launch.return_value = mock_browser

        mock_playwright.return_value.__enter__.return_value = mock_p

        # Mock storage
        mock_storage.save.return_value = "pdfs/test.pdf"

        # 커스텀 PDF 옵션
        custom_options = {
            "format": "Letter",
            "print_background": False,
        }

        # 실행
        file_path, expiry_date = self.generator.generate_pdf(
            url="https://example.com",
            pdf_options=custom_options,
        )

        # 검증 - 커스텀 옵션으로 PDF 생성
        mock_page.pdf.assert_called_once_with(**custom_options)


class CustomPDFGenerator(BasePDFGenerator):
    """테스트용 커스텀 PDF Generator"""

    def get_default_url(self):
        return "https://custom.example.com"

    def get_viewport_size(self):
        return {"width": 1280, "height": 720}

    def get_pdf_format(self):
        return "Letter"


@pytest.mark.django_db
class CustomPDFGeneratorTests(TestCase):
    """커스텀 PDF Generator 테스트"""

    def setUp(self):
        """테스트 설정"""
        self.generator = CustomPDFGenerator()

    def test_custom_default_url(self):
        """커스텀 기본 URL 테스트"""
        url = self.generator.get_default_url()
        self.assertEqual(url, "https://custom.example.com")

    def test_custom_viewport_size(self):
        """커스텀 뷰포트 크기 테스트"""
        viewport = self.generator.get_viewport_size()
        self.assertEqual(viewport["width"], 1280)
        self.assertEqual(viewport["height"], 720)

    def test_custom_pdf_format(self):
        """커스텀 PDF 포맷 테스트"""
        pdf_format = self.generator.get_pdf_format()
        self.assertEqual(pdf_format, "Letter")

    @patch("reports.services.base_pdf_generator.sync_playwright")
    @patch("reports.services.base_pdf_generator.default_storage")
    def test_generate_pdf_uses_default_url(self, mock_storage, mock_playwright):
        """기본 URL 사용 테스트"""
        # Mock Playwright
        mock_page = Mock()
        mock_page.pdf.return_value = b"fake_pdf_content"

        mock_browser = Mock()
        mock_browser.new_page.return_value = mock_page

        mock_p = Mock()
        mock_p.chromium.launch.return_value = mock_browser

        mock_playwright.return_value.__enter__.return_value = mock_p

        # Mock storage
        mock_storage.save.return_value = "pdfs/test.pdf"

        # URL을 제공하지 않음
        file_path, expiry_date = self.generator.generate_pdf()

        # 검증 - 기본 URL 사용
        mock_page.goto.assert_called_once_with("https://custom.example.com", wait_until="networkidle")
