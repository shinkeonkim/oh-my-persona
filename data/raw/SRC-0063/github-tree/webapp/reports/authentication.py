from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework import authentication, exceptions

from users.models import BotToken


class ReportBotAuthentication(authentication.BaseAuthentication):
    """
    BOT 토큰을 사용한 인증 클래스
    HTTP 헤더의 X-BOT-TOKEN을 확인하여 해당 레포트의 사용자로 인증합니다.
    """

    keyword = "X-BOT-TOKEN"
    header_name = "HTTP_X_BOT_TOKEN"

    def authenticate(self, request):
        """
        HTTP 헤더에서 BOT 토큰을 추출하고 검증하여 사용자를 인증합니다.

        Args:
            request: DRF Request 객체

        Returns:
            tuple: (user, token) 또는 None
        """
        # 헤더에서 토큰 추출
        bot_token = self.get_token_from_request(request)

        if bot_token is None:
            return None

        return self.authenticate_credentials(bot_token)

    def get_token_from_request(self, request):
        """
        Request 객체에서 BOT 토큰을 추출합니다.
        X-BOT-TOKEN 헤더 또는 쿼리 파라미터에서 토큰을 찾습니다.

        Args:
            request: DRF Request 객체

        Returns:
            str: 토큰 문자열 또는 None
        """
        # HTTP 헤더에서 토큰 확인
        token = request.META.get(self.header_name)

        if token:
            return token

        # 쿼리 파라미터에서 토큰 확인 (fallback)
        token = request.query_params.get("BOT_TOKEN")

        return token

    def authenticate_credentials(self, token):
        """
        토큰을 검증하고 해당 레포트의 사용자를 반환합니다.

        Args:
            token: BOT 토큰 문자열

        Returns:
            tuple: (user, token)

        Raises:
            AuthenticationFailed: 토큰이 유효하지 않은 경우
        """
        # verify_token 메서드 사용하여 사용자 정보와 유효성 확인
        user, is_valid = BotToken.verify_token(token)

        if not is_valid or user is None:
            raise exceptions.AuthenticationFailed("Invalid BOT token")

        if not user.is_active:
            raise exceptions.AuthenticationFailed("User inactive or deleted")

        return (user, token)

    def authenticate_header(self, request):
        """
        WWW-Authenticate 헤더 값을 반환합니다.

        Args:
            request: DRF Request 객체

        Returns:
            str: WWW-Authenticate 헤더 값
        """
        return self.keyword


class ReportBotAuthenticationScheme(OpenApiAuthenticationExtension):
    """
    drf-spectacular를 위한 ReportBotAuthentication 스키마 확장
    """

    target_class = "reports.authentication.ReportBotAuthentication"
    name = "ReportBotAuthentication"

    def get_security_definition(self, auto_schema):  # noqa: ARG002
        """
        OpenAPI 스키마의 보안 정의를 반환합니다.
        """
        return {
            "type": "apiKey",
            "in": "header",
            "name": "X-BOT-TOKEN",
            "description": "BOT 토큰을 사용한 인증. 쿼리 파라미터 BOT_TOKEN으로도 전달 가능합니다.",
        }
