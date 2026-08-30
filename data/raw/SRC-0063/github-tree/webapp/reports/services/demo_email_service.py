"""
Demo Email Service

title과 content를 받아서 이메일을 전송하는 데모 서비스입니다.
"""

from reports.services.email.base_email_service import BaseEmailService


class DemoEmailService(BaseEmailService):
    """
    데모 이메일 전송 서비스

    Usage:
        service = DemoEmailService()
        result = service.send_email(
            to_email="singun11@gmail.com",
            title="테스트 제목",
            content="테스트 내용입니다."
        )
    """

    def get_subject(self, **kwargs) -> str:
        """
        이메일 제목을 반환합니다.

        Args:
            **kwargs: title 파라미터를 포함해야 합니다.

        Returns:
            str: 이메일 제목
        """
        title = kwargs.get("title", "제목 없음")
        return title

    def get_body(self, **kwargs) -> str:
        """
        이메일 본문을 반환합니다.

        Args:
            **kwargs: content 파라미터를 포함해야 합니다.

        Returns:
            str: 이메일 본문
        """
        content = kwargs.get("content", "내용 없음")
        return content
