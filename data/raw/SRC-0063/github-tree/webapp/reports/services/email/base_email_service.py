"""
Base Email Service

이메일 전송을 위한 베이스 서비스 클래스입니다.
이 클래스를 상속하여 특정 제목, 내용, 첨부 파일 등을 지정한 서비스를 만들 수 있습니다.
"""

import logging
from abc import ABC, abstractmethod
from email.mime.image import MIMEImage
from typing import Optional

from django.conf import settings
from django.core.mail import EmailMessage

logger = logging.getLogger(__name__)


class BaseEmailService(ABC):
    """
    이메일 전송을 위한 베이스 클래스

    Usage:
        class MyEmailService(BaseEmailService):
            def get_subject(self, **kwargs):
                return "Welcome to My Service"

            def get_body(self, **kwargs):
                return "Thank you for signing up!"

        service = MyEmailService()
        result = service.send_email(to_email="user@example.com")
    """

    def get_from_email(self) -> str:
        """
        발신자 이메일 주소를 반환합니다.
        하위 클래스에서 오버라이드하여 커스터마이징할 수 있습니다.

        Returns:
            str: 발신자 이메일 주소
        """
        return settings.DEFAULT_FROM_EMAIL

    @abstractmethod
    def get_subject(self, **kwargs) -> str:
        """
        이메일 제목을 반환합니다.
        하위 클래스에서 반드시 구현해야 합니다.

        Args:
            **kwargs: 제목 생성에 필요한 추가 파라미터

        Returns:
            str: 이메일 제목
        """
        pass

    @abstractmethod
    def get_body(self, **kwargs) -> str:
        """
        이메일 본문을 반환합니다.
        하위 클래스에서 반드시 구현해야 합니다.

        Args:
            **kwargs: 본문 생성에 필요한 추가 파라미터

        Returns:
            str: 이메일 본문
        """
        pass

    def get_html_body(self, **kwargs) -> Optional[str]:
        """
        HTML 형식의 이메일 본문을 반환합니다.
        하위 클래스에서 오버라이드하여 HTML 이메일을 전송할 수 있습니다.

        Args:
            **kwargs: 본문 생성에 필요한 추가 파라미터

        Returns:
            Optional[str]: HTML 형식의 이메일 본문 (None이면 일반 텍스트만 전송)
        """
        return None

    def get_attachments(self, **kwargs) -> list[tuple[str, bytes, str]]:
        """
        첨부 파일 목록을 반환합니다.
        하위 클래스에서 오버라이드하여 첨부 파일을 추가할 수 있습니다.

        Args:
            **kwargs: 첨부 파일 생성에 필요한 추가 파라미터

        Returns:
            list[tuple[str, bytes, str]]: 첨부 파일 목록
            각 튜플은 (파일명, 파일 내용, MIME 타입) 형식
        """
        return []

    def get_reply_to(self) -> Optional[list[str]]:
        """
        Reply-To 이메일 주소 목록을 반환합니다.
        하위 클래스에서 오버라이드하여 커스터마이징할 수 있습니다.

        Returns:
            Optional[list[str]]: Reply-To 이메일 주소 목록
        """
        return None

    def get_cc(self, **kwargs) -> Optional[list[str]]:
        """
        CC 이메일 주소 목록을 반환합니다.
        하위 클래스에서 오버라이드하여 커스터마이징할 수 있습니다.

        Args:
            **kwargs: CC 주소 생성에 필요한 추가 파라미터

        Returns:
            Optional[list[str]]: CC 이메일 주소 목록
        """
        return None

    def get_bcc(self, **kwargs) -> Optional[list[str]]:
        """
        BCC 이메일 주소 목록을 반환합니다.
        하위 클래스에서 오버라이드하여 커스터마이징할 수 있습니다.

        Args:
            **kwargs: BCC 주소 생성에 필요한 추가 파라미터

        Returns:
            Optional[list[str]]: BCC 이메일 주소 목록
        """
        return None

    def get_inline_images(self, **kwargs) -> list[tuple[str, bytes, str, str]]:
        """
        HTML 본문에 인라인으로 포함할 이미지 목록을 반환합니다.
        하위 클래스에서 오버라이드하여 인라인 이미지를 추가할 수 있습니다.

        Args:
            **kwargs: 이미지 생성에 필요한 추가 파라미터

        Returns:
            list[tuple[str, bytes, str, str]]: 인라인 이미지 목록
            각 튜플은 (Content-ID, 파일 내용, MIME 타입, 파일명) 형식
        """
        return []

    def send_email(
        self,
        to_email: str,
        **kwargs,
    ) -> dict:
        """
        이메일을 전송합니다.

        Args:
            to_email: 수신자 이메일 주소
            **kwargs: 제목, 본문, 첨부 파일 생성에 필요한 추가 파라미터

        Returns:
            dict: {
                "success": bool,
                "message": str,
            }
        """
        try:
            # 이메일 구성 요소 생성
            subject = self.get_subject(**kwargs)
            body = self.get_body(**kwargs)
            html_body = self.get_html_body(**kwargs)
            from_email = self.get_from_email()
            reply_to = self.get_reply_to()
            cc = self.get_cc(**kwargs)
            bcc = self.get_bcc(**kwargs)

            # EmailMessage 객체 생성
            email = EmailMessage(
                subject=subject,
                body=body,
                from_email=from_email,
                to=[to_email],
                cc=cc,
                bcc=bcc,
                reply_to=reply_to,
            )

            # HTML 본문이 있으면 추가
            if html_body:
                email.content_subtype = "html"
                email.body = html_body

            # 첨부 파일 추가
            attachments = self.get_attachments(**kwargs)
            for filename, content, mimetype in attachments:
                email.attach(filename, content, mimetype)

            # 인라인 이미지 추가 (CID 방식)
            inline_images = self.get_inline_images(**kwargs)
            for cid, content, mimetype, filename in inline_images:
                # MIMEImage 객체 생성
                mime_image = MIMEImage(content)
                mime_image.add_header("Content-ID", f"<{cid}>")
                mime_image.add_header("Content-Disposition", "inline", filename=filename)
                # EmailMessage의 attachments 리스트에 직접 추가
                email.attach(mime_image)

            # 이메일 전송
            email.send()

            logger.info(f"Email sent successfully to {to_email}")
            return {
                "success": True,
                "message": "Email sent successfully",
            }

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e!s}", exc_info=True)
            return {
                "success": False,
                "message": f"Failed to send email: {e!s}",
            }
