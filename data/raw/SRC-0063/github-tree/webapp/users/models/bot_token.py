import secrets

from django.db import models
from django.utils.translation import gettext_lazy as _

from common.models import BaseModel

from .user import User


class BotToken(BaseModel):
    """
    BOT 토큰 모델
    PDF 생성 등 자동화 프로세스를 위한 일회용 인증 토큰
    """

    class Meta:
        db_table = "bot_tokens"
        verbose_name = _("BOT 토큰")
        verbose_name_plural = _("BOT 토큰")
        ordering = ["-created_at"]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bot_tokens",
        null=False,
        blank=False,
        verbose_name=_("사용자"),
        help_text=_("이 토큰과 연관된 사용자"),
    )
    token = models.CharField(
        max_length=100,
        unique=True,
        null=False,
        blank=False,
        verbose_name=_("토큰"),
        help_text=_("BOT 인증을 위한 토큰 문자열"),
    )

    def __str__(self):
        return f"BOT Token for {self.user.email} ({self.token})"

    @staticmethod
    def generate_token() -> str:
        """
        임시 비밀번호 문자열 생성 (X-BOT-TOKEN-임의문자열 50 길이)

        Returns:
            str: X-BOT-TOKEN- 접두사를 포함한 총 62자리 토큰
        """
        random_string = secrets.token_urlsafe(37)  # 약 50자 정도의 URL-safe 문자열 생성
        return f"X-BOT-TOKEN-{random_string[:50]}"

    @classmethod
    def create_for_report(cls, user):
        """
        특정 레포트에 대한 BOT 토큰 생성 및 저장

        Args:
            user: User 모델 인스턴스

        Returns:
            BotToken: 생성된 토큰 인스턴스
        """
        token = cls.generate_token()
        return cls.objects.create(user=user, token=token)

    @classmethod
    def verify_token(cls, token: str):
        """
        토큰이 유효한지 검증하고 사용자 정보 반환

        Args:
            token: 검증할 토큰 문자열

        Returns:
            Tuple[Optional[AbstractBaseUser], bool]: (사용자 객체 또는 None, 유효 여부)
        """
        try:
            bot_token = cls.objects.get(token=token)
            return (bot_token.user, True)
        except cls.DoesNotExist:
            return (None, False)

    @classmethod
    def verify_and_consume_token(cls, token: str):
        """
        토큰을 검증하고, 검증 성공 시 해당 토큰을 삭제 (일회용)

        Args:
            token: 검증할 토큰 문자열

        Returns:
            Tuple[Optional[AbstractBaseUser], bool]: (사용자 객체 또는 None, 유효 여부)
        """
        try:
            bot_token = cls.objects.get(token=token)
            user = bot_token.user
            bot_token.delete()
            return (user, True)
        except cls.DoesNotExist:
            return (None, False)

    def consume(self):
        """
        토큰을 사용 처리 (삭제)
        """
        self.delete()
