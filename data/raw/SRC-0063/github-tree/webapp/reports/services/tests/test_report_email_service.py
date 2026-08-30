from unittest.mock import Mock, mock_open, patch

from django.test import TestCase, override_settings

import pytest
from reports.services.report_email_service import ReportEmailService


@pytest.mark.django_db
class ReportEmailServiceTests(TestCase):
    """ReportEmailService 테스트"""

    def setUp(self):
        """테스트 설정"""
        self.service = ReportEmailService()
        self.test_email = "test@example.com"
        self.test_url = "https://example.com/report"

    def test_get_subject(self):
        """이메일 제목 생성 테스트"""
        subject = self.service.get_subject(site_name="깜빡이")
        self.assertEqual(subject, "[깜빡이] 집중력 분석 레포트가 도착했습니다")

    def test_get_subject_with_custom_site_name(self):
        """커스텀 사이트 이름으로 제목 생성 테스트"""
        subject = self.service.get_subject(site_name="테스트사이트")
        self.assertEqual(subject, "[테스트사이트] 집중력 분석 레포트가 도착했습니다")

    def test_get_body(self):
        """이메일 본문 생성 테스트 (텍스트 형식은 제공하지 않음)"""
        body = self.service.get_body()
        self.assertEqual(body, "")

    def test_get_html_body(self):
        """HTML 이메일 본문 생성 테스트"""
        html_body = self.service.get_html_body(site_url=self.test_url)

        self.assertIn("<!DOCTYPE html>", html_body)
        self.assertIn("집중력 분석 레포트", html_body)
        self.assertIn("깜빡이팀", html_body)
        self.assertIn("cid:logo", html_body)

    @override_settings(STATIC_ROOT="/fake/static/")
    @patch("builtins.open", mock_open(read_data=b"fake_logo_data"))
    @patch("os.path.join", return_value="/fake/static/logo.png")
    def test_get_inline_images_with_logo(self, mock_path_join):
        """로고 이미지 인라인 포함 테스트"""
        inline_images = self.service.get_inline_images()

        self.assertEqual(len(inline_images), 1)
        cid, content, mimetype, filename = inline_images[0]
        self.assertEqual(cid, "logo")
        self.assertEqual(content, b"fake_logo_data")
        self.assertEqual(mimetype, "image/png")
        self.assertEqual(filename, "logo.png")

    @override_settings(STATIC_ROOT="/fake/static/")
    @patch("builtins.open", side_effect=FileNotFoundError)
    @patch("os.path.join", return_value="/fake/static/logo.png")
    def test_get_inline_images_logo_not_found(self, mock_path_join, mock_open_file):
        """로고 파일이 없을 때 테스트"""
        inline_images = self.service.get_inline_images()

        # 로고를 찾을 수 없어도 빈 리스트 반환 (오류 없음)
        self.assertEqual(len(inline_images), 0)

    @patch("reports.services.email.file_attachment_email_service.default_storage")
    def test_get_attachments_with_pdf(self, mock_storage):
        """PDF 첨부 파일 포함 테스트"""
        mock_storage.exists.return_value = True
        mock_storage.open.return_value.__enter__.return_value.read.return_value = b"fake_pdf_data"

        attachments = self.service.get_attachments(
            pdf_file_path="/path/to/report.pdf",
            pdf_filename="my_report.pdf",
        )

        self.assertEqual(len(attachments), 1)
        filename, content, mimetype = attachments[0]
        self.assertEqual(filename, "my_report.pdf")
        self.assertEqual(content, b"fake_pdf_data")
        self.assertEqual(mimetype, "application/pdf")

    def test_get_attachments_without_pdf_path(self):
        """PDF 경로가 제공되지 않았을 때 테스트"""
        attachments = self.service.get_attachments()

        self.assertEqual(len(attachments), 0)

    @patch("reports.services.email.file_attachment_email_service.default_storage")
    def test_get_attachments_file_not_found(self, mock_storage):
        """PDF 파일을 찾을 수 없을 때 테스트"""
        mock_storage.exists.return_value = False

        attachments = self.service.get_attachments(
            pdf_file_path="/path/to/missing.pdf",
        )

        self.assertEqual(len(attachments), 0)

    @patch("reports.services.report_email_service.BasePDFGenerator")
    @patch.object(ReportEmailService, "send_email")
    def test_send_report_email_generates_pdf(self, mock_send_email, mock_pdf_generator_class):
        """PDF를 생성하고 이메일 전송 테스트"""
        # Mock PDF generator
        mock_generator = Mock()
        mock_generator.generate_pdf.return_value = (
            "/path/to/generated.pdf",
            "2024-12-31",
        )
        mock_pdf_generator_class.return_value = mock_generator

        # Mock send_email
        mock_send_email.return_value = {
            "success": True,
            "message": "Email sent successfully",
        }

        # 실행
        result = self.service.send_report_email(
            to_email=self.test_email,
            site_url=self.test_url,
        )

        # 검증
        self.assertTrue(result["success"])
        self.assertEqual(result["pdf_file_path"], "/path/to/generated.pdf")

        # PDF 생성 호출 확인
        mock_generator.generate_pdf.assert_called_once_with(url=self.test_url)

        # 이메일 전송 호출 확인
        mock_send_email.assert_called_once()

    @patch.object(ReportEmailService, "send_email")
    def test_send_report_email_with_existing_pdf(self, mock_send_email):
        """기존 PDF 파일로 이메일 전송 테스트"""
        # Mock send_email
        mock_send_email.return_value = {
            "success": True,
            "message": "Email sent successfully",
        }

        # 실행 - 이미 생성된 PDF 경로 제공
        result = self.service.send_report_email(
            to_email=self.test_email,
            site_url=self.test_url,
            pdf_file_path="/path/to/existing.pdf",
        )

        # 검증
        self.assertTrue(result["success"])
        self.assertEqual(result["pdf_file_path"], "/path/to/existing.pdf")

        # 이메일 전송 호출 확인
        mock_send_email.assert_called_once()

    @patch("reports.services.report_email_service.BasePDFGenerator")
    def test_send_report_email_pdf_generation_fails(self, mock_pdf_generator_class):
        """PDF 생성 실패 시 처리 테스트"""
        # Mock PDF generator - 예외 발생
        mock_generator = Mock()
        mock_generator.generate_pdf.side_effect = Exception("PDF generation failed")
        mock_pdf_generator_class.return_value = mock_generator

        # 실행
        result = self.service.send_report_email(
            to_email=self.test_email,
            site_url=self.test_url,
        )

        # 검증 - 실패 반환
        self.assertFalse(result["success"])
        self.assertIn("Failed to send report email", result["message"])

    @patch("reports.services.report_email_service.BasePDFGenerator")
    @patch.object(ReportEmailService, "send_email")
    def test_send_report_email_with_custom_filename(self, mock_send_email, mock_pdf_generator_class):
        """커스텀 PDF 파일명으로 이메일 전송 테스트"""
        # Mock PDF generator
        mock_generator = Mock()
        mock_generator.generate_pdf.return_value = ("/path/to/pdf", "2024-12-31")
        mock_pdf_generator_class.return_value = mock_generator

        # Mock send_email
        mock_send_email.return_value = {
            "success": True,
            "message": "Email sent successfully",
        }

        # 실행
        result = self.service.send_report_email(
            to_email=self.test_email,
            site_url=self.test_url,
            pdf_filename="custom_report.pdf",
        )

        # 검증
        self.assertTrue(result["success"])

        # send_email 호출 시 pdf_filename 전달 확인
        call_kwargs = mock_send_email.call_args[1]
        self.assertEqual(call_kwargs["pdf_filename"], "custom_report.pdf")
