from json.decoder import JSONDecodeError

import requests
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from api.v1.account.adapters import CustomKakaoOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings
from django.http import JsonResponse
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from user.models import User

KAKAO_CALLBACK_URI = settings.KAKAO_CALLBACK_URI
BASE_URL = settings.BASE_URL


def kakao_login(request):
    rest_api_key = getattr(settings, "KAKAO_REST_API_KEY")
    from django.shortcuts import redirect

    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={rest_api_key}&redirect_uri={KAKAO_CALLBACK_URI}&response_type=code"
    )


class KakaoAuthRequestSerializer(serializers.Serializer):
    code = serializers.CharField(help_text="카카오 OAuth 인증 후 반환되는 인가 코드")


class KakaoAuthResponseSerializer(serializers.Serializer):
    access = serializers.CharField(help_text="JWT Access Token")
    refresh = serializers.CharField(help_text="JWT Refresh Token")


@extend_schema(
    summary="Kakao OAuth Callback",
    description="카카오 인증 후 받은 인가 코드(code)를 이용해 액세스 토큰을 요청하고, 회원가입 또는 로그인 처리를 합니다.",
    parameters=[
        OpenApiParameter(
            name="code",
            description="카카오 OAuth 인증 후 반환되는 인가 코드",
            required=True,
            type=str,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="redirect_uri",
            description="redirect_uri",
            required=False,
            type=str,
            location=OpenApiParameter.QUERY,
        ),
    ],
    request=KakaoAuthRequestSerializer,  # 요청 스키마
    responses={
        200: KakaoAuthResponseSerializer,  # 응답 스키마
        400: {
            "description": "잘못된 요청",
            "content": {
                "application/json": {"example": {"err_msg": "failed to signin"}}
            },
        },
    },
    examples=[
        OpenApiExample(
            "성공 예제",
            summary="정상적으로 JWT 토큰을 반환하는 경우",
            value={"access": "jwt_access_token", "refresh": "jwt_refresh_token"},
            response_only=True,
        ),
        OpenApiExample(
            "실패 예제",
            summary="인가 코드가 올바르지 않은 경우",
            value={"err_msg": "failed to retrieve access token"},
            response_only=True,
        ),
    ],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def kakao_callback(request):
    rest_api_key = getattr(settings, "KAKAO_REST_API_KEY")
    code = request.GET.get("code")
    redirect_uri = request.GET.get("redirect_uri", KAKAO_CALLBACK_URI)
    """
    Access Token Request
    """
    token_req = requests.get(
        f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={rest_api_key}&redirect_uri={redirect_uri}&code={code}"
    )
    token_req_json = token_req.json()
    error = token_req_json.get("error")
    if error is not None:
        error_code = token_req_json.get("error_code")
        error_description = token_req_json.get("error_description")
        raise JSONDecodeError(error, doc=token_req.text, pos=0)
    access_token = token_req_json.get("access_token")
    """
    Email Request
    """
    profile_request = requests.get(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    profile_json = profile_request.json()
    kakao_account = profile_json.get("kakao_account")
    email = kakao_account.get("email")

    """
    Signup or Signin Request
    """
    try:
        user = User.objects.get(email=email)
        # 기존에 가입된 유저의 Provider가 kakao가 아니면 에러 발생, 맞으면 로그인
        # 다른 SNS로 가입된 유저
        social_user = SocialAccount.objects.get(user=user)
        if social_user is None:
            return JsonResponse(
                {"err_msg": "email exists but not social user"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if social_user.provider != "kakao":
            return JsonResponse(
                {"err_msg": "no matching social type"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = {"access_token": access_token, "code": code}

        accept = requests.post(
            f"{BASE_URL}api/v1/accounts/kakao/login/finish/?redirect_uri={redirect_uri}",
            data=data,
        )

        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({"err_msg": "failed to signin"}, status=accept_status)
        accept_json = accept.json()
        accept_json.pop("user", None)
        return JsonResponse(accept_json)
    except User.DoesNotExist:
        data = {"access_token": access_token, "code": code}
        accept = requests.post(
            f"{BASE_URL}api/v1/accounts/kakao/login/finish/?redirect_uri={redirect_uri}",
            data=data,
        )

        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({"err_msg": "failed to signup"}, status=accept_status)
        accept_json = accept.json()
        accept_json.pop("user", None)
        return JsonResponse(accept_json)


class KakaoLogin(SocialLoginView):
    adapter_class = CustomKakaoOAuth2Adapter
    client_class = OAuth2Client
    callback_url = None

    def post(self, request, *args, **kwargs):
        self.request = request
        self.callback_url = request.query_params.get("redirect_uri", KAKAO_CALLBACK_URI)
        self.serializer = self.get_serializer(data=self.request.data)

        self.serializer.is_valid(raise_exception=True)
        self.login()
        return self.get_response()
