"""
레포트 이메일 전송 Celery Task

PDF 레포트를 비동기로 생성하고 이메일로 전송하는 celery task입니다.
"""

import logging
from typing import Optional

from celery import shared_task
from reports.services import ReportEmailService

from users.models import BotToken

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    name="reports.send_report_email",
    max_retries=3,
    default_retry_delay=60,  # 1분
)
def send_report_email_task(
    self,
    to_email: str,
    site_url: str,
    pdf_file_path: Optional[str] = None,
    pdf_filename: str = "깜빡이 집중력 분석 레포트.pdf",
    site_name: str = "깜빡이",
    bot_token_id: Optional[int] = None,
) -> dict:
    """
    PDF 레포트를 비동기로 생성하고 이메일로 전송합니다.

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

    Example:
        # Django shell에서 실행:
        from reports.tasks import send_report_email_task
        result = send_report_email_task.delay(
            to_email="user@example.com",
            site_url="https://example.com/report",
        )
        print(result.get())  # 결과 대기 및 출력
    """
    try:
        logger.info(
            f"Starting send_report_email_task: to_email={to_email}, "
            f"site_url={site_url}, pdf_file_path={pdf_file_path}"
        )

        # 이메일 서비스 인스턴스 생성
        service = ReportEmailService()

        # 레포트 이메일 전송
        result = service.send_report_email(
            to_email=to_email,
            site_url=site_url,
            pdf_file_path=pdf_file_path,
            pdf_filename=pdf_filename,
            site_name=site_name,
        )

        bot_token = BotToken.objects.filter(id=bot_token_id).first()
        if bot_token:
            bot_token.consume()

        if result["success"]:
            logger.info(f"Report email sent successfully to {to_email}")
        else:
            logger.warning(f"Failed to send report email to {to_email}: {result['message']}")

        return result

    except Exception as exc:
        logger.error(f"Error in send_report_email_task: {exc!s}", exc_info=True)

        # 재시도 로직
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying send_report_email_task (attempt {self.request.retries + 1})")
            raise self.retry(exc=exc)

        # 최대 재시도 횟수 초과 시 실패 반환
        logger.error(f"Max retries exceeded for send_report_email_task to {to_email}")
        return {
            "success": False,
            "message": f"Failed to send report email after {self.max_retries} retries: {exc!s}",
        }


@shared_task(
    bind=True,
    name="reports.send_report_email_with_existing_pdf",
    max_retries=3,
    default_retry_delay=60,
)
def send_report_email_with_existing_pdf_task(
    self,
    to_email: str,
    site_url: str,
    pdf_file_path: str,
    pdf_filename: str = "report.pdf",
    site_name: str = "깜빡이",
) -> dict:
    """
    이미 생성된 PDF 파일을 이메일로 전송합니다.

    Args:
        to_email: 수신자 이메일 주소
        site_url: 레포트 사이트 URL
        pdf_file_path: PDF 파일 경로
        pdf_filename: PDF 첨부 파일명 (기본값: report.pdf)
        site_name: 사이트 이름 (기본값: 깜빡이)

    Returns:
        dict: {
            "success": bool,
            "message": str,
            "pdf_file_path": str,  # 성공 시 PDF 파일 경로
        }

    Example:
        # Django shell에서 실행:
        from reports.tasks import send_report_email_with_existing_pdf_task
        result = send_report_email_with_existing_pdf_task.delay(
            to_email="user@example.com",
            site_url="https://example.com/report",
            pdf_file_path="pdfs/2025/01/01/abc123.pdf",
        )
        print(result.get())
    """
    try:
        logger.info(
            f"Starting send_report_email_with_existing_pdf_task: to_email={to_email}, pdf_file_path={pdf_file_path}"
        )

        # 이메일 서비스 인스턴스 생성
        service = ReportEmailService()

        # 레포트 이메일 전송 (기존 PDF 사용)
        result = service.send_report_email(
            to_email=to_email,
            site_url=site_url,
            pdf_file_path=pdf_file_path,
            pdf_filename=pdf_filename,
            site_name=site_name,
        )

        if result["success"]:
            logger.info(f"Report email with existing PDF sent successfully to {to_email}")
        else:
            logger.warning(f"Failed to send report email with existing PDF to {to_email}: {result['message']}")

        return result

    except Exception as exc:
        logger.error(f"Error in send_report_email_with_existing_pdf_task: {exc!s}", exc_info=True)

        # 재시도 로직
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying send_report_email_with_existing_pdf_task (attempt {self.request.retries + 1})")
            raise self.retry(exc=exc)

        # 최대 재시도 횟수 초과 시 실패 반환
        logger.error(f"Max retries exceeded for send_report_email_with_existing_pdf_task to {to_email}")
        return {
            "success": False,
            "message": f"Failed to send report email after {self.max_retries} retries: {exc!s}",
        }
