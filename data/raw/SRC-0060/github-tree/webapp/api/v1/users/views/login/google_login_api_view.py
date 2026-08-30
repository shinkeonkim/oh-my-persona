"""
Google OAuth 2.0 Login View using dj-rest-auth.

This module provides a simplified Google login implementation using dj-rest-auth's
built-in SocialLoginView, which leverages django-allauth's GoogleOAuth2Adapter.

This approach is more maintainable and follows Django/DRF best practices compared
to manual OAuth implementation.
"""

import logging

from django.conf import settings

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from drf_spectacular.utils import OpenApiExample, extend_schema

from ...serializers.login_response_serializer import LoginResponseSerializer
from ...serializers.oauth_login_request_serializer import OAuthLoginRequestSerializer

logger = logging.getLogger(__name__)


class GoogleLoginAPIView(SocialLoginView):
  """
    Google OAuth 2.0 Login API View.

    This view uses dj-rest-auth's SocialLoginView with django-allauth's
    GoogleOAuth2Adapter to handle the complete OAuth flow:

    1. Receives authorization code from frontend
    2. Exchanges code for access token with Google
    3. Retrieves user info from Google
    4. Creates/updates user and SocialAccount
    5. Returns JWT tokens

    The OAuth2Client and adapter handle all the complexity of token exchange,
    user creation, and session management automatically.

    **Important Note about redirect_uri:**
    The redirect_uri from the request is used to instantiate the OAuth2Client.
    This allows frontend applications to use different callback URLs (e.g.,
    localhost for development, production domain for prod) as long as they're
    registered in Google Cloud Console.
    """

  adapter_class = GoogleOAuth2Adapter
  client_class = OAuth2Client
  serializer_class = OAuthLoginRequestSerializer
  callback_url = settings.GOOGLE_CALLBACK_URI
  permission_classes = []
  authentication_classes = []  # Disable authentication for public OAuth endpoint

  @extend_schema(
    operation_id="google_login",
    tags=["Authentication"],
    summary="Google OAuth 2.0 Login",
    description=("Exchange Google authorization code for JWT tokens and user information.\n\n"
                 "This endpoint uses dj-rest-auth and django-allauth to handle the OAuth flow:\n"
                 "- Validates the authorization code with Google\n"
                 "- Creates or retrieves the user account\n"
                 "- Links the Google account via SocialAccount\n"
                 "- Returns JWT access and refresh tokens\n\n"
                 "**OAuth Flow:**\n"
                 "1. Frontend redirects user to Google OAuth authorization URL with redirect_uri\n"
                 "2. User authorizes the app on Google\n"
                 "3. Google redirects back to your redirect_uri with authorization code\n"
                 "4. Frontend sends code (and optionally redirect_uri) to this endpoint\n"
                 "5. Backend exchanges code for tokens and returns JWT\n\n"
                 "**Dynamic Redirect URI Support:**\n"
                 "You can provide a custom `redirect_uri` in the request body.\n"
                 "This is useful when:\n"
                 "- Using different domains for dev/staging/prod\n"
                 "- Supporting multiple frontend applications\n"
                 "- Using mobile deep links\n\n"
                 "**Important:** The redirect_uri MUST be registered in Google Cloud Console.\n"),
    request=OAuthLoginRequestSerializer,
    responses={
      200: LoginResponseSerializer,
      400: {
        "description": "Invalid authorization code or OAuth error",
        "content": {
          "application/json": {
            "example": {
              "error": "invalid_grant",
              "error_description": "Authorization code is invalid or expired",
            }
          }
        },
      },
      422: {
        "description": "Validation error"
      },
      500: {
        "description": "Internal server error"
      },
    },
    examples=[
      OpenApiExample(
        name="Basic Login (Default Redirect URI)",
        description="Login using the default redirect URI from settings",
        value={"code": "4/0AY0e-g5example_google_code"},
        request_only=True,
      ),
      OpenApiExample(
        name="Login with Custom Redirect URI (Development)",
        description="Useful for local development with custom ports",
        value={
          "code": "4/0AY0e-g5example_google_code",
          "redirect_uri": "http://localhost:3000/auth/google/callback",
        },
        request_only=True,
      ),
      OpenApiExample(
        name="Login with Custom Redirect URI (Production)",
        description="Production domain redirect URI",
        value={
          "code": "4/0AY0e-g5example_google_code",
          "redirect_uri": "https://myapp.com/auth/google/callback",
        },
        request_only=True,
      ),
      OpenApiExample(
        name="Login with Mobile Deep Link",
        description="Mobile app deep link redirect URI",
        value={
          "code": "4/0AY0e-g5example_google_code",
          "redirect_uri": "com.myapp://auth/google/callback",
        },
        request_only=True,
      ),
      OpenApiExample(
        name="Successful Login Response",
        description="JWT tokens and user information returned on successful login",
        value={
          "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
          "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
          "user": {
            "id": 1,
            "email": "user@gmail.com",
            "username": "google_user",
            "social_account": [{
              "provider": "google",
              "uid": "1234567890"
            }],
          },
        },
        response_only=True,
      ),
    ],
  )
  def post(self, request, *args, **kwargs):
    """
        Handle Google OAuth login request.

        The parent SocialLoginView handles:
        - Validating the authorization code
        - Token exchange with Google (using the redirect_uri)
        - User info retrieval
        - User creation/update
        - JWT token generation
        """
    # IMPORTANT: Update callback_url attribute BEFORE calling super().post()
    # The serializer reads view.callback_url directly via getattr()
    redirect_uri = request.data.get("redirect_uri", "")
    if redirect_uri:
      self.callback_url = redirect_uri
      logger.info(f"Using custom redirect_uri: {redirect_uri}")
    else:
      logger.info(f"Using default callback_url: {self.callback_url}")

    return super().post(request, *args, **kwargs)
