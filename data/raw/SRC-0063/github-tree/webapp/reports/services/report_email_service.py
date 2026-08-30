"""
Report Email Service

PDF 레포트를 이메일로 전송하는 서비스입니다.
"""

import logging
import os
from typing import Optional

from django.conf import settings

from reports.services.base_pdf_generator import BasePDFGenerator
from reports.services.email import FileAttachmentEmailService

logger = logging.getLogger(__name__)


class ReportEmailService(FileAttachmentEmailService):
    """
    PDF 레포트를 생성하고 이메일로 전송하는 서비스

    Usage:
        service = ReportEmailService()
        result = service.send_report_email(
            to_email="user@example.com",
            site_url="https://example.com/report",
        )
    """

    def get_subject(self, **kwargs) -> str:
        """
        이메일 제목을 반환합니다.

        Args:
            **kwargs: 제목 생성에 필요한 추가 파라미터
                - site_name: 사이트 이름 (선택)

        Returns:
            str: 이메일 제목
        """
        site_name = kwargs.get("site_name", "깜빡이")
        return f"[{site_name}] 집중력 분석 레포트가 도착했습니다"

    def get_body(self, **kwargs) -> str:
        """
        이메일 본문을 반환합니다. / 텍스트 형식 제공하지 않음.
        """
        return ""

    def get_html_body(self, **kwargs) -> Optional[str]:
        """
        HTML 형식의 이메일 본문을 반환합니다.

        Args:
            **kwargs: 본문 생성에 필요한 추가 파라미터
                - site_url: 사이트 URL (선택)

        Returns:
            Optional[str]: HTML 형식의 이메일 본문
        """
        html_body = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="font-family: 'Malgun Gothic', '맑은 고딕', sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #ffffff;">
    <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #ffffff;">
        <tr>
            <td align="center" style="padding: 20px;">
                <table width="800" border="0" cellspacing="0" cellpadding="0" style="max-width: 800px;">
                    <!-- Header -->
                    <tr>
                        <td align="center" style="background-color: #FFE3A7; padding: 20px; border-radius: 5px 5px 0 0;">
                            <img src="cid:logo" alt="깜빡이 로고" style="max-width: 200px; height: auto; display: block; margin: 0 auto;">
                        </td>
                    </tr>
                    <!-- Content -->
                    <tr>
                        <td align="center" style="background-color: #FFF4DF; padding: 30px; border-left: 1px solid #ddd; border-right: 1px solid #ddd; border-bottom: 1px solid #ddd; border-radius: 0 0 5px 5px; font-size: 1.5em;">
                            <p style="margin: 0 0 15px 0;">안녕하세요,</p>
                            <p style="margin: 0 0 15px 0;">집중력 분석 레포트가 도착했습니다.</p>
                            <p style="margin: 0 0 15px 0;">첨부된 PDF 파일을 확인해 주세요.</p>
                            <p style="margin: 0;">감사합니다.</p>
                        </td>
                    </tr>
                    <!-- Footer -->
                    <tr>
                        <td align="center" style="padding-top: 20px; color: #888; font-size: 12px;">
                            <p style="margin: 0;">@깜빡이팀</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
        return html_body

    def get_inline_images(self, **kwargs) -> list[tuple[str, bytes, str, str]]:
        """
        HTML 본문에 인라인으로 포함할 이미지 목록을 반환합니다.

        Returns:
            list[tuple[str, bytes, str, str]]: 인라인 이미지 목록
            각 튜플은 (Content-ID, 파일 내용, MIME 타입, 파일명) 형식
        """
        inline_images = []

        # 로고 이미지 경로
        logo_path = os.path.join(settings.STATIC_ROOT, "logo.png")

        try:
            # 로고 이미지 읽기
            with open(logo_path, "rb") as f:
                logo_content = f.read()

            # CID는 'logo'로 설정 (HTML에서 cid:logo로 참조)
            inline_images.append(("logo", logo_content, "image/png", "logo.png"))
            logger.info(f"Logo image loaded successfully from {logo_path}")

        except FileNotFoundError:
            logger.warning(f"Logo file not found at {logo_path}")
        except Exception as e:
            logger.error(f"Failed to load logo image: {e}", exc_info=True)

        return inline_images

    def get_attachments(self, **kwargs) -> list[tuple[str, bytes, str]]:
        """
        첨부 파일 목록을 반환합니다.

        Args:
            **kwargs: 첨부 파일 생성에 필요한 추가 파라미터
                - pdf_file_path: PDF 파일 경로 (필수)
                - pdf_filename: PDF 파일명 (선택, 기본값: report.pdf)

        Returns:
            list[tuple[str, bytes, str]]: 첨부 파일 목록
        """
        pdf_file_path = kwargs.get("pdf_file_path")
        pdf_filename = kwargs.get("pdf_filename", "report.pdf")

        if not pdf_file_path:
            logger.warning("No PDF file path provided for email attachment")
            return []

        try:
            attachment = self.attach_file_from_storage(
                file_path=pdf_file_path, filename=pdf_filename, mimetype="application/pdf"
            )
            return [attachment]
        except FileNotFoundError as e:
            logger.error(f"PDF file not found: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to attach PDF file: {e}", exc_info=True)
            return []

    def send_report_email(
        self,
        to_email: str,
        site_url: str,
        pdf_file_path: Optional[str] = None,
        pdf_filename: str = "report.pdf",
        site_name: str = "깜빡이",
    ) -> dict:
        """
        PDF 레포트를 생성하고 이메일로 전송합니다.

        Args:
            to_email: 수신자 이메일 주소
            site_url: 레포트를 생성할 사이트 URL
            pdf_file_path: 이미 생성된 PDF 파일 경로 (선택, None이면 site_url로부터 새로 생성)
            pdf_filename: PDF 첨부 파일명 (기본값: report.pdf)
            site_name: 사이트 이름 (기본값: 깜빡이)

        Returns:
            dict: {
                "success": bool,
                "message": str,
                "pdf_file_path": str,  # 성공 시 PDF 파일 경로
            }
        """
        try:
            # PDF 파일이 제공되지 않은 경우 생성
            if not pdf_file_path:
                logger.info(f"Generating PDF for URL: {site_url}")
                generator = BasePDFGenerator()
                pdf_file_path, expiry_date = generator.generate_pdf(url=site_url)
                logger.info(f"PDF generated successfully: {pdf_file_path}, expires at {expiry_date}")

            # 이메일 전송
            result = self.send_email(
                to_email=to_email,
                site_url=site_url,
                site_name=site_name,
                pdf_file_path=pdf_file_path,
                pdf_filename=pdf_filename,
            )

            if result["success"]:
                result["pdf_file_path"] = pdf_file_path

            return result

        except Exception as e:
            logger.error(f"Failed to send report email: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Failed to send report email: {e!s}",
            }
