import logging
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import render

import requests
from allauth.socialaccount.models import SocialAccount
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from common.exceptions.custom_exceptions import InternalServerError
from common.schemas.error_schemas import (
    get_internal_server_error_schema,
    get_validation_error_schema,
)
from common.views.base_api_view import BaseAPIView
from users.models import log_login_attempt

from ..exceptions.user_exceptions import InvalidCredentialsError
from ..schemas.error_schemas import get_external_service_error_schema
from ..serializers.kakao_auth_request_serializer import KakaoAuthRequestSerializer
from ..serializers.user_detail_serializer import UserDetailSerializer

User = get_user_model()
logger = logging.getLogger(__name__)


class KakaoLoginView(BaseAPIView):
    permission_classes = [AllowAny]
    serializer_class = KakaoAuthRequestSerializer
    authentication_classes = []

    @extend_schema(
        operation_id="kakao_login",
        tags=["Authentication"],
        summary="Kakao OAuth 2.0 Login",
        description="Exchange Kakao authorization code for JWT tokens and user information.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Kakao OAuth authorization code received from frontend",
                    },
                    "redirectUri": {
                        "type": "string",
                        "description": "Redirect URI used in OAuth flow (optional, falls back to default)",
                        "format": "uri",
                    },
                },
                "required": ["code"],
            }
        },
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "accessToken": {
                            "type": "string",
                            "description": "JWT access token",
                        },
                        "refreshToken": {
                            "type": "string",
                            "description": "JWT refresh token",
                        },
                        "user": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer", "description": "User ID"},
                                "email": {
                                    "type": "string",
                                    "description": "User email address",
                                },
                                "username": {
                                    "type": "string",
                                    "description": "User username",
                                },
                                "socialAccount": {
                                    "type": "array",
                                    "description": "Connected social accounts",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "provider": {
                                                "type": "string",
                                                "description": "Social provider name",
                                            },
                                            "uid": {
                                                "type": "string",
                                                "description": "Social provider user ID",
                                            },
                                        },
                                    },
                                },
                                "ticketAmount": {
                                    "type": "integer",
                                    "description": "Available ticket count",
                                },
                                "usedTicketAmount": {
                                    "type": "integer",
                                    "description": "Used ticket count",
                                },
                                "isIntroCompleted": {
                                    "type": "boolean",
                                    "description": "Whether user completed introduction",
                                },
                            },
                        },
                    },
                },
                description="Login successful",
                examples=[
                    OpenApiExample(
                        name="Successful login response",
                        value={
                            "accessToken": "access_token",
                            "refreshToken": "refresh_token",
                            "user": {
                                "id": 733,
                                "email": "shinkeonkim@kakao.com",
                                "username": "김신건",
                                "socialAccount": [{"provider": "kakao", "uid": "4440977096"}],
                                "ticketAmount": 28,
                                "usedTicketAmount": 12,
                                "isIntroCompleted": False,
                            },
                        },
                        status_codes=[200],
                    )
                ],
            ),
            400: get_external_service_error_schema(),
            422: get_validation_error_schema(),
            500: get_internal_server_error_schema(),
        },
        examples=[
            OpenApiExample(
                "Basic Login Example",
                value={"code": "authorization_code_here"},
                request_only=True,
            ),
            OpenApiExample(
                "Login with Custom Redirect URI",
                value={
                    "code": "authorization_code_here",
                    "redirectUri": "https://myapp.com/auth/kakao/callback",
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        authorization_code = request.data.get("code")
        redirect_uri = request.data.get("redirect_uri") or settings.KAKAO_CALLBACK_URI

        if not authorization_code:
            log_login_attempt(request, "failure", error_message="Authorization code is required")
            raise InvalidCredentialsError("Authorization code is required")

        kakao_user_info = None
        kakao_id = None
        email = None

        try:
            # 카카오 토큰 획득
            logger.info("Attempting to get Kakao access token for authorization code")
            kakao_token_info = self.get_kakao_access_token(authorization_code, redirect_uri)
            if not kakao_token_info:
                from ..exceptions.user_exceptions import ExternalServiceError

                logger.warning("Failed to get Kakao access token")
                log_login_attempt(request, "failure", error_message="Failed to get Kakao access token")
                raise ExternalServiceError("Failed to get Kakao access token")

            # 카카오 사용자 정보 획득
            logger.info("Attempting to get Kakao user info")
            kakao_user_info = self.get_kakao_user_info(kakao_token_info["access_token"])
            if not kakao_user_info:
                from ..exceptions.user_exceptions import ExternalServiceError

                logger.warning("Failed to get Kakao user info")
                log_login_attempt(request, "failure", error_message="Failed to get Kakao user info")
                raise ExternalServiceError("Failed to get Kakao user info")

            # 사용자 정보 추출
            kakao_id = str(kakao_user_info["id"])
            email = kakao_user_info.get("kakao_account", {}).get("email", "")
            logger.info(f"Processing Kakao login for user ID: {kakao_id}")

            # 사용자 생성 또는 조회
            user = self.get_or_create_user(kakao_user_info)

            # JWT 토큰 생성
            refresh = RefreshToken.for_user(user)

            # 성공 로그 기록
            logger.info(f"Successful Kakao login for user: {user.username} (ID: {user.id})")
            log_login_attempt(request, "success", user=user, email=email, kakao_id=kakao_id)

            user_serializer = UserDetailSerializer(user)

            return Response(
                {
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                    "user": user_serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            from common.exceptions.custom_exceptions import InternalServerError

            # 에러 로그 기록
            error_message = str(e)
            logger.error(f"Error during Kakao login process: {error_message}", exc_info=True)
            log_login_attempt(
                request,
                "error",
                email=email if email else "",
                kakao_id=kakao_id if kakao_id else "",
                error_message=error_message,
            )
            raise InternalServerError(
                message="Authentication service error",
                details={"error": error_message},
            )

    def get_kakao_access_token(self, authorization_code, redirect_uri):
        client_id = settings.KAKAO_REST_API_KEY
        client_secret = settings.KAKAO_SECRET_KEY

        token_url = "https://kauth.kakao.com/oauth/token"

        data = {
            "grant_type": "authorization_code",
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "code": authorization_code,
        }

        response = requests.post(token_url, data=data)

        if response.status_code == 200:
            return response.json()
        else:
            logger.error("Error getting Kakao access token")
            logger.error(response.text)
            return None

    def get_kakao_user_info(self, access_token):
        user_info_url = "https://kapi.kakao.com/v2/user/me"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        }

        response = requests.get(user_info_url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            logger.error("Error getting Kakao user info")
            logger.error(response.text)
            return None

    def get_or_create_user(self, kakao_user_info):
        kakao_id = str(kakao_user_info["id"])
        email = kakao_user_info.get("kakao_account", {}).get("email", "")
        nickname = kakao_user_info.get("properties", {}).get("nickname", "")

        # 먼저 kakao_id로 기존 사용자 확인
        try:
            user = User.objects.get(kakao_id=kakao_id)
            # 기존 사용자 정보 업데이트
            if email and user.email != email:
                user.email = email
                user.save()
            return user
        except User.DoesNotExist:
            pass

        # SocialAccount로도 확인
        try:
            social_account = SocialAccount.objects.get(provider="kakao", uid=kakao_id)
            return social_account.user
        except SocialAccount.DoesNotExist:
            pass

        # 이메일로 기존 사용자 확인
        if email and User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            # OAuth 정보 추가
            user.kakao_id = kakao_id
            user.save()
        else:
            # 새 사용자 생성
            username = nickname if nickname else f"kakao_{kakao_id}"
            counter = 0
            original_username = username

            while User.objects.filter(username=username).exists():
                counter += 1
                username = f"{original_username}_{counter}"

            user = User.objects.create_user(
                email=email if email else f"kakao_{kakao_id}@kakao.local",
                username=username,
                phone_number="",  # 카카오에서 전화번호는 제공하지 않으므로 빈 값
                kakao_id=kakao_id,
            )

        # SocialAccount 생성 (아직 없다면)
        if not SocialAccount.objects.filter(user=user, provider="kakao").exists():
            SocialAccount.objects.create(user=user, provider="kakao", uid=kakao_id, extra_data=kakao_user_info)

        return user


class TokenRefreshView(BaseAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        operation_id="token_refresh",
        tags=["Authentication"],
        summary="Refresh JWT Token",
        description="Generate a new access token using a valid refresh token."
        + "If token rotation is enabled, a new refresh token will also be provided.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "refreshToken": {
                        "type": "string",
                        "description": "JWT refresh token",
                    }
                },
                "required": ["refreshToken"],
            }
        },
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "accessToken": {
                            "type": "string",
                            "description": "New JWT access token",
                        },
                        "refreshToken": {
                            "type": "string",
                            "description": "New JWT refresh token (if rotation enabled)",
                        },
                    },
                },
                description="Token refresh successful",
                examples=[
                    OpenApiExample(
                        name="Token refresh response",
                        value={
                            "access_token": "access_token",
                            "refresh_token": "refresh_token",
                        },
                        status_codes=[200],
                    )
                ],
            ),
            400: get_validation_error_schema(),
            401: get_validation_error_schema(),
        },
        examples=[
            OpenApiExample(
                "Token refresh request",
                value={"refreshToken": "refresh_token_here"},
                request_only=True,
            )
        ],
    )
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token", "")
            if not refresh_token:
                raise InvalidCredentialsError("Refresh token is required")

            refresh = RefreshToken(refresh_token)

            response_data = {"access_token": str(refresh.access_token)}

            # If token rotation is enabled, provide new refresh token
            if getattr(settings, "SIMPLE_JWT", {}).get("ROTATE_REFRESH_TOKENS", False):
                # Get user from token
                user_id = refresh.payload.get("user_id")
                user = User.objects.get(id=user_id)

                # Blacklist old token
                refresh.blacklist()

                # Create new refresh token
                new_refresh = RefreshToken.for_user(user)
                response_data["refresh_token"] = str(new_refresh)

            return Response(response_data, status=status.HTTP_200_OK)

        except TokenError as e:
            raise InvalidCredentialsError(
                message="Invalid token",
                details={"error": str(e)},
            )
        except Exception as e:
            logger.error(f"Error during token refresh: {e}")
            raise InvalidCredentialsError("Invalid token")


class LogoutView(BaseAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        operation_id="logout",
        tags=["Authentication"],
        summary="Logout User",
        description="Blacklist the refresh token to securely logout the user. "
        + "Once blacklisted, the token cannot be used for authentication.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "refreshToken": {
                        "type": "string",
                        "description": "JWT refresh token to blacklist",
                    }
                },
                "required": ["refreshToken"],
            }
        },
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {"message": {"type": "string", "description": "Success message"}},
                },
                description="Logout successful",
                examples=[
                    OpenApiExample(
                        name="Successful logout",
                        value={"message": "Successfully logged out"},
                        status_codes=[200],
                    )
                ],
            ),
            400: get_validation_error_schema(),
            500: get_internal_server_error_schema(),
        },
        examples=[
            OpenApiExample(
                "Logout request",
                value={"refreshToken": "refresh_token_here"},
                request_only=True,
            )
        ],
    )
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
            else:
                raise InvalidCredentialsError("Refresh token is required")
        except TokenError as e:
            logger.error("Token error during logout")
            logger.error(e)
            raise InvalidCredentialsError(
                message="Invalid token",
                details={"error": str(e)},
            )
        except Exception as e:
            logger.error(f"Error during logout: {e}")
            raise InternalServerError(
                message="Logout failed",
                details={"error": str(e)},
            )


class KakaoTestView(BaseAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(exclude=True)  # Exclude from API documentation
    def get(self, request):
        client_id = settings.KAKAO_REST_API_KEY
        redirect_uri = getattr(
            settings,
            "KAKAO_TEST_CALLBACK_URI",
            "http://localhost:8000/api/v1/users/kakao/test/callback/",
        )

        if not client_id:
            return render(request, "kakao_test_config_error.html")

        # 카카오 OAuth 인증 URL 생성
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "profile_nickname,profile_image,account_email",
        }

        auth_url = f"https://kauth.kakao.com/oauth/authorize?{urlencode(params)}"

        context = {
            "auth_url": auth_url,
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": "profile_nickname,profile_image,account_email",
        }

        return render(request, "kakao_test.html", context)


class KakaoTestCallbackView(BaseAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(exclude=True)  # Exclude from API documentation
    def get(self, request):
        code = request.GET.get("code")
        error = request.GET.get("error")
        error_description = request.GET.get("error_description", "")

        if error:
            context = {"error": error, "error_description": error_description}
            return render(request, "kakao_test_callback_error.html", context)

        if not code:
            return render(request, "kakao_test_callback_error.html")

        redirect_uri = getattr(
            settings,
            "KAKAO_TEST_CALLBACK_URI",
            "http://localhost:8000/api/v1/users/kakao/test/callback/",
        )
        context = {"code": code, "redirect_uri": redirect_uri}
        return render(request, "kakao_test_callback_success.html", context)
