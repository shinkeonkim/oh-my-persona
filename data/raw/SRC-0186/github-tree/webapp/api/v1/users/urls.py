from django.conf import settings
from django.urls import path

from .views import (
    KakaoLoginView,
    KakaoTestCallbackView,
    KakaoTestView,
    LogoutView,
    TokenRefreshView,
    UserView,
    nice_verification_init_api,
    nice_verification_verify_api,
    registration_statistics_api,
)

app_name = "api.v1.users"

urlpatterns = [
    path("", UserView.as_view(), name="user-detail"),
    # OAuth Authentication
    path("kakao/login/", KakaoLoginView.as_view(), name="kakao_login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path(
        "statistics/",
        registration_statistics_api,
        name="registration_statistics_api",
    ),
    # NICE API 본인인증 REST API
    path(
        "nice/init/",
        nice_verification_init_api,
        name="nice_verification_init_api",
    ),
    path(
        "nice/verify/",
        nice_verification_verify_api,
        name="nice_verification_verify_api",
    ),
]

if settings.DEBUG:
    urlpatterns += [
        path("kakao/test/", KakaoTestView.as_view(), name="kakao_test"),
        path(
            "kakao/test/callback/",
            KakaoTestCallbackView.as_view(),
            name="kakao_test_callback",
        ),
    ]
