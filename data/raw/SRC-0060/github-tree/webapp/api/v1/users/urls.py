"""
URL patterns for users API endpoints.

This module defines all authentication and user management related endpoints.

URL Structure:
- /api/v1/users/...

Authentication Endpoints:
- Social Login (OAuth2)
- Token Management
- Test Views (development only)
"""

from django.urls import path

from .views.login.google_login_api_view import GoogleLoginAPIView
from .views.login.google_test_callback_view import GoogleTestCallbackView
from .views.login.google_test_view import GoogleTestView
from .views.login.kakao_login_api_view import KakaoLoginAPIView
from .views.login.kakao_test_callback_view import KakaoTestCallbackView
from .views.login.kakao_test_view import KakaoTestView
from .views.logout_api_view import LogoutAPIView
from .views.token_refresh_api_view import TokenRefreshAPIView

app_name = "users"

urlpatterns = [
  # ========== Social Login (OAuth2) ==========
  # Kakao OAuth2 Login
  path(
    "kakao/login/",
    KakaoLoginAPIView.as_view(),
    name="kakao-login",
  ),
  # Google OAuth2 Login
  path(
    "google/login/",
    GoogleLoginAPIView.as_view(),
    name="google-login",
  ),
  # ========== Token Management ==========
  # Logout (blacklist refresh token)
  path(
    "logout/",
    LogoutAPIView.as_view(),
    name="logout",
  ),
  # Refresh access token
  path(
    "token/refresh/",
    TokenRefreshAPIView.as_view(),
    name="token-refresh",
  ),
  # ========== Test Views (Development Only) ==========
  # Kakao OAuth test page (renders HTML)
  path(
    "kakao/test/",
    KakaoTestView.as_view(),
    name="kakao-test",
  ),
  # Kakao OAuth callback handler (for testing)
  path(
    "kakao/test/callback/",
    KakaoTestCallbackView.as_view(),
    name="kakao-test-callback",
  ),
  # Google OAuth test page (renders HTML)
  path(
    "google/test/",
    GoogleTestView.as_view(),
    name="google-test",
  ),
  # Google OAuth callback handler (for testing)
  path(
    "google/test/callback/",
    GoogleTestCallbackView.as_view(),
    name="google-test-callback",
  ),
]
